import win32com.client
import pythoncom
import os
from datetime import datetime
from re import compile

class Mail_Outlook():
    def __init__(self):
        # win32com 호출 및 MAPI(Messaging Application Program Interface) 사용
        self.outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        
        # 해당 계정의 받은 편지함
        self.receiveMailbox = self.outlook.GetDefaultFolder(6)     # 받은 편지함 6

        # 해당 계정의 최상위 폴더
        self.root_Folder = self.outlook.Folders.Item(1)

    # 메일함 생성(결과를 True/False 반환)
    def create_mailbox(self, Name):
        # 첨부 파일이 저장될 폴더명 = 메일함명
        self.download_Place = Name

        try:
            self.root_Folder.Folders.Add(Name)  # 메일함 생성
            res = True

        except pythoncom.com_error as error:
            res = False
        
        # RPA 용 메일함 주소값 반환
        self.rpa_Mailbox = self.root_Folder.Folders[Name]

        return res


    # 메일함 선택, 해당 메일함의 주소값 반환
    def select_mailbox(self, Name):
        return self.root_Folder.Folders[Name]


    # 특정 메일 검색 후 해당 메일의 주소값 반환
    def search_mail(self, Mailbox, SenderName, Subject, SenderEmailAddress = None):
        # 메일들의 정보를 가지고 있는 인스턴스 주소값
        findItem = Mailbox.Items

        # 특정 메일 찾기(보낸이, 보낸 사람의 email address, 제목) / 주소값 반환
        # 속성값은 https://docs.microsoft.com/ko-kr/office/vba/api/outlook.mailitem 참고
        try:
            if SenderEmailAddress != None:
                matchMail = findItem.Find("[SenderName] = '{}' and [SenderEmailAddress] = '{}' and [Subject] = '{}'".format(SenderName, SenderEmailAddress, Subject))
            else:
                matchMail = findItem.Find("[SenderName] = '{}' and [Subject] = '{}'".format(SenderName, Subject))
            return matchMail
        
        except AttributeError:  # 해당 메일이 없을 경우
            return False


    # 메일을 다른 폴더로 메일 이동(이동할 기본폴더는 RPA용 메일함), 실패시 False 반환
    def move_mail(self, MatchMail, Mailbox = None):

        if Mailbox == None:
            Mailbox = self.rpa_Mailbox

        try:
            # 메일을 메일함으로 이동
            MatchMail.Move(Mailbox)
            return True

        except AttributeError:  # 메일 이동 실패
            return False

    
    # 첨부 파일 다운로드 (기본값은 RPA용 메일함, 기준 시간으로 판별, 기본값 3시간)
    # 다운받은 첨부파일 이름 리스트 반환, 첨부파일 없는 경우 -1, 기준 시간 미만에 해당하는 메일이 없는 경우 -2 반환
    def download_attachment(self, Mailbox = None, standardTime = 3):

        if Mailbox == None:
            Mailbox = self.rpa_Mailbox

        # 현재 날짜
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")

        items = Mailbox.Items

        # 최근 메일 가져오기
        targetMail = items.GetLast()

        # 메일 수신 날짜
        receiveDate = targetMail.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S")
        receiveDate = datetime.strptime(receiveDate,"%Y-%m-%d %H:%M:%S")

        # 현재시간과 메일 수신시간 차이 계산
        time_Differ = now -  receiveDate
        time_Differ = round(time_Differ.seconds / 3600)
        
        # 메일 수신시간이 기준시간 내 수신한 메일일 경우 첨부파일 다운로드
        if time_Differ < standardTime:

            # 메일의 첨부파일 개수
            numOfAttachment = targetMail.Attachments.Count      # 첨부파일의 개수

            # 첨부 파일이 없을 경우
            if numOfAttachment == 0:
                return -1

            # 첨부파일이 저장될 경로 및 폴더 생성
            path = os.getcwd() + "\\" + self.download_Place
            os.makedirs(path, exist_ok = True)
            fileName = []

            # 첨부 파일 저장
            for i in range(1, numOfAttachment + 1):
                targetMail.Attachments.Item(i).SaveAsFile(path + "\\" + targetMail.Attachments.Item(i).FileName)
                file = "첨부파일 : " + targetMail.Attachments.Item(i).FileName + " 저장 완료"
                fileName.append(file)

            return fileName     # 다운받은 첨부파일 이름의 리스트 반환

        else:
            return -2   # 기준 시간 미만에 해당하는 메일이 없는 경우


    # 메일 발송(받는 사람, 참조, 첨부파일은 리스트로 전달, 올바른 메일주소만 필터링)
    # 메일 발송 성공시 True, 실패시 False 반환
    def send_mail(self, Subject, Content, To = [], CC = [], Atch = []):

        # Outlook Object Model 불러오기
        new_Mail = win32com.client.Dispatch("Outlook.Application").CreateItem(0)

        # 메일 주소 정규 표현식
        checkAddress = compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        correctTo = ""
        correctCC = ""

        # 받는 사람 메일 주소 검사 후, 올바른 메일주소로만 이루어진 메일주소 문지열 생성
        if To:
            for addr in To:
                res = checkAddress.match(addr)
                if res != None:
                    correctTo = correctTo + addr + ";"

        # 참조 메일 주소 검사 후, 올바른 메일주소로만 이루어진 메일주소 문지열 생성
        if CC:
            for addr in CC:
                res = checkAddress.match(addr)
                if res != None:
                    correctCC = correctCC + addr + ";"
        
        # 메일 수신자
        new_Mail.To = correctTo

        # 메일 참조
        new_Mail.CC = correctCC

        # 메일 제목
        new_Mail.Subject = Subject

        # 메일 내용
        new_Mail.HTMLBody = Content

        # 첨부파일 추가
        if Atch:
            for atchFile in Atch:
                new_Mail.Attachments.Add(atchFile)

        try:
            # 메일 발송
            new_Mail.Send()
            return True

        except pythoncom.com_error as error:    # 메일 보내기 실패시
            return False


    # 검색한 메일의 정보 반환(메일 제목), 검색한 메일이 없는 경우 False 반환
    def get_subject(self, mail):
        try:
            return mail.Subject

        except AttributeError:
            return False
    

    # 검색한 메일의 정보 반환(보낸 사람 Email 주소), 검색한 메일이 없는 경우 False 반환
    def get_sender_addr(self, mail):
        
        try:
            # ExchangeService 사용하는 경우
            if mail.SenderEmailType == "EX":
                return mail.Sender.GetExchangeUser().PrimarySmtpAddress
            else:
                return mail.SenderEmailAddress

        except AttributeError:
            return False

    
    # 검색한 메일의 정보 반환(받는 사람 Email 주소), 검색한 메일이 없는 경우 False 반환
    def get_recipient_addr(self, mail):
        
        try:
            # 받는 사람(수신인)들의 Email 주소를 리스트로 반환
            recipients = mail.Recipients
            recipients_list = []

            # recipient 인스턴스들을 가지고 있는 리스트 생성
            for recip in recipients:
                recipients_list.append(recip)   

            address_list = []

            # 각 recipient 인스턴스로부터 Email 주소 가져오기
            for recip in recipients_list:
                address_list.append(recip.AddressEntry.GetExchangeUser().PrimarySmtpAddress)

            return address_list

        except AttributeError:
            return False

    
    # 검색한 메일의 정보 반환(수신 날짜), 검색한 메일이 없는 경우 False 반환
    def get_receive_time(self, mail):
        try:
            return mail.ReceivedTime

        except AttributeError:
            return False

    
    # 검색한 메일의 정보 반환(메일 내용 HTML 태그 포함), 검색한 메일이 없는 경우 False 반환
    def get_html_body(self, mail):
        try:
            return mail.HTMLBody

        except AttributeError:
            return False

    
    # 검색한 메일의 정보 반환(메일 내용 HTML 태그 미포함), 검색한 메일이 없는 경우 False 반환
    def get_body(self, mail):
        try:
            return mail.Body
        
        except AttributeError:
            return False

