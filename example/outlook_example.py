from sk_optom import outlook
from sk_optom import rpalms

# LMS 인스턴스 생성
lms = rpalms.RPA_LMS("logstash")

# 인스턴스 생성
oMail = outlook.Mail_Outlook()

# RPA용 메일함 생성
oMail.create_mailbox("RPA Folder")

# 특정 메일 검색(보낸 사람, 보낸 사람의 이메일 주소, 메일 제목)
mail = oMail.search_mail(Mailbox = oMail.receiveMailbox, SenderName = "sender name", SenderEmailAddress = "test@abcd.com", Subject = "subject")

# 특정 메일 검색(보낸 사람, 메일 제목)
mail = oMail.search_mail(Mailbox = oMail.receiveMailbox, SenderName = "sender name", Subject = "subject")

# 특정 메일의 콘텐츠 조회
# 검색한 메일이 없는 경우 False 반환
print(oMail.get_subject(mail))          # 해당 메일의 제목 반환
print(oMail.get_body(mail))             # 해당 메일의 내용을 Text로 반환
print(oMail.get_html_body(mail))        # 해당 메일의 내용을 HTML 형식으로 반환
print(oMail.get_receive_time(mail))     # 해당 메일의 수신 날짜 반환
print(oMail.get_sender_addr(mail))      # 해당 메일을 보낸 사람의 Email Address 반환
print(oMail.get_recipient_addr(mail))   # 해당 메일을 받는 사람들의 Email Address를 리스트로 반환

# 다른 폴더로 메일 이동, 성공시 True / 실패시 False 반환
if oMail.move_mail(mail):
    lms.sendLog_InfoLevel("메일을 이동하였습니다.")
else:
    lms.sendLog_ErrorLevel("메일 이동 실패")

# 첨부파일 다운로드(기준시간으로 판별, 수신 시간이 3시간 미만인 메일일 경우 첨부파일 다운로드, 기본값은 RPA용 메일함)
# 다운받은 첨부파일 이름 리스트 반환, 첨부파일 없는 경우 -1, 기준 시간 미만에 해당하는 메일이 없는 경우 -2 반환
download_file_list = oMail.download_attachment(Mailbox = None, standardTime = 3)

if download_file_list == -1:
    lms.sendLog_InfoLevel("해당 메일에 첨부파일이 없습니다.")

elif download_file_list == -2:
    lms.sendLog_ErrorLevel("기준시간 미만에 해당하는 메일이 없습니다.")

# Mail 항목
content = """<br><img src="D:\\test\\RPA_image.png">"""     # 본문 내용
subject = "메일 보내기 테스트 1"                            # 메일 제목
to = ["RPA1@sk.com", "RPA2@sk.com"]                        # 받는 사람
cc = ["RPA3@sk.com", "RPA4@sk.com"]                        # 참조
filePath = [r"file path 1", r"file path 2"]                # 첨부파일 경로

# 메일 발송(받는 사람, 참조, 첨부파일은 리스트로 전달, 올바른 메일주소만 필터링)
# 메일 발송 성공시 True, 실패시 False 반환
if oMail.send_mail(To = to, Subject = subject, Content = content, CC = cc, Atch = filePath):
    lms.sendLog_InfoLevel("메일 발송 완료")
else:
    lms.sendLog_ErrorLevel("메일 발송 실패")

# 메일함 선택, 해당 메일함의 주소값 반환
mailBox = oMail.select_mailbox("메일함 이름")


# EX) Test 메일함에서 홍길동이 보낸 RPA Test라는 메일을 찾아서 RPA 메일함으로 이동하기
outlook = outlook.Mail_Outlook()
testMailBox = outlook.select_mailbox("Test")
matchMail = outlook.search_mail(Mailbox = testMailBox, SenderName = "홍길동", Subject = "RPA Test")
RPAMailBox = outlook.select_mailbox("RPA")
outlook.move_mail(MatchMail = matchMail, Mailbox = RPAMailBox)
