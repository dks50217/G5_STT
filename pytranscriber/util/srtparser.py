import re, sys, json

class SRTParser(object):
    @staticmethod
    def extractTextFromSRT(fileSRT):
        file_name = fileSRT
        file_encoding = 'utf-8'

        #loop through the lines for parsing
        with open(file_name, encoding=file_encoding, errors='replace') as f:
            lines = f.readlines()
            new_lines = SRTParser.clean_up(lines)
            new_file_name = file_name[:-4] + '.txt'

        #write parsed txt file
        with open(new_file_name, 'w', encoding=file_encoding) as f:
            for line in new_lines:
                f.write(line)

    @staticmethod
    def clean_up(lines):
        regexSubtitleIndexNumber = re.compile("[0-9]+")

        new_lines = []
        for line in lines[1:]:
            #if line empty or
            #if line contains --> or
            #if line matches the subtitle index regex
            #then skip line
            if (not line or not line.strip()) or ("-->" in line) or regexSubtitleIndexNumber.match(line):
                continue
            else:
                #append line
                new_lines.append(line)
        return new_lines
    #one Json or RC record
    @staticmethod
    def parseSRTToJson(fileSRT,audioList):
        srt_filename = fileSRT
        out_filename = fileSRT[:-4] + '.json'
        srt = open(srt_filename, 'r',encoding="utf-8").read()
        parsed_srt = SRTParser.parse_srt(srt,fileSRT)
       
        if isinstance(audioList,dict) == True:
           jsonparent = SRTParser.addJsonParent(audioList,parsed_srt)
           open(out_filename, 'w',encoding="utf-8").write(json.dumps(jsonparent, indent=2, sort_keys=True, ensure_ascii=False))
        else:
           open(out_filename, 'w',encoding="utf-8").write(json.dumps(parsed_srt, indent=2, sort_keys=True, ensure_ascii=False))
    @staticmethod
    def parsePairSRTToJson(pairList,audioList):
        srt_filename1 = pairList[0]
        srt_filename2 = pairList[1]
        out_filename = pairList[0][:-4].replace('-in','') + '.json'
        srt1 = open(srt_filename1, 'r',encoding="utf-8").read()
        srt2 = open(srt_filename2, 'r',encoding="utf-8").read()
        parsed_srt1 = SRTParser.parse_srt(srt1,srt_filename1)
        parsed_srt2 = SRTParser.parse_srt(srt2,srt_filename2)
        mergedList = parsed_srt1 + parsed_srt2
        sortedList = SRTParser.sortList(mergedList)

        if isinstance(audioList,dict) == True:
            jsonparent = SRTParser.addJsonParent(audioList,sortedList)
            open(out_filename, 'w',encoding="utf-8").write(json.dumps(jsonparent, indent=2, sort_keys=True, ensure_ascii=False))
        else:
            open(out_filename, 'w',encoding="utf-8").write(json.dumps(sortedList, indent=2, sort_keys=True, ensure_ascii=False))
          
    @staticmethod
    def parse_time(time_string):
        hours = int(re.findall(r'(\d+):\d+:\d+,\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+,\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+),\d+', time_string)[0])
        milliseconds = int(re.findall(r'\d+:\d+:\d+,(\d+)', time_string)[0])
        return (hours*3600 + minutes*60 + seconds) * 1000 + milliseconds

    @staticmethod
    def addJsonParent(audioList,parsed_srt):
        from datetime import datetime
        ParentList = []
        now = datetime.now()

        if audioList.get('CallID',0):
            call_id =  audioList.get('CallID')
            record_id = audioList.get('RecordId')
            user_id = audioList.get('UserId')
            call_detail_id = audioList.get('CallDetailId')
            call_log_id = audioList.get('CallLogId')
            project_id = audioList.get('ProjectId')
            talkingBeginTime = audioList.get('TalkingBeginTime')
            talkingEndTime = audioList.get('TalkingEndTime')
            ParentList.append({
                'CallID': call_id,
                'RecordID': record_id, 
                'UserID':user_id,
                'CallDetailID': call_detail_id,
                'CallLogID': call_log_id,
                'TalkingBeginTime':talkingBeginTime.strftime("%Y/%m/%d, %H:%M:%S"),
                'TalkingEndTime':talkingEndTime.strftime("%Y/%m/%d, %H:%M:%S"),
                'ProjectID': project_id,
                'ChatList': parsed_srt,
                'TransDate': now.strftime("%Y/%m/%d, %H:%M:%S")
            })

        elif audioList.get('MessageID',0):
            message_id = audioList.get('MessageID')
            serviceGUID = audioList.get('ServiceGUID')
            ParentList.append({
                'MessageID': message_id,
                'ChatList': parsed_srt,
                'serviceGUID': serviceGUID,
                'TransDate': now.strftime("%Y/%m/%d, %H:%M:%S")
            })

        return ParentList
    @staticmethod
    def parse_srt(srt_string,fileSRT):
        
        if 'in' in fileSRT:
            srt_type = 1
        else :
            srt_type = 2
        
        srt_list = []
        for line in srt_string.split('\n\n'):
            if line != '':
                index = int(re.match(r'\d+', line).group())
                pos = re.search(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', line).end() + 1
                content = line[pos:]
                start_time_string = re.findall(r'(\d+:\d+:\d+,\d+) --> \d+:\d+:\d+,\d+', line)[0]
                end_time_string = re.findall(r'\d+:\d+:\d+,\d+ --> (\d+:\d+:\d+,\d+)', line)[0]
                start_time = start_time_string
                end_time = end_time_string
                time_diff = SRTParser.parse_time(end_time) - SRTParser.parse_time(start_time)
                time_diff_str = SRTParser.dotInsert(str(time_diff),1)
                #20200728 Michael 時序顛倒問題，改用一個對話完成
                sort_key = SRTParser.parse_time(end_time)
                # type = 1:in 2:out
                srt_list.append( {
                    # 'index': index, 
                    'content': content,
                    'start': start_time,
                    'end': end_time,
                    'diff': time_diff_str,
                    'type': srt_type,
                    'sortkey': sort_key
                } )

        return srt_list

    @staticmethod
    def dotInsert(str, position) -> 'str':
        length = len(str)
        if(length < 4):
            return '0.'+ str[:position] + str[position:]
        if (position > length or position < 0):
            return str
        return str[:position] + '.' + str[position:]

    @staticmethod
    def sortList(unSortList):
        sortedList = sorted(unSortList, key = lambda x : x['start'])   
        return sortedList




