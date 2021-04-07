import logging
import logstash
import sys
import socket
import platform
import psutil
import multiprocessing as mp
import time

# RPA LMS 로그 관리 모듈
class RPA_LMS:
    def __init__(self, category, port = 5900, info_Path = r"./log/info.log", result_Path = r"./log/result.log"):   # category는 logfile(.log 파일), logstash(python-logstash 모듈) 2가지 지원

        self.category = category
        self.proc = mp.current_process()                # 현재 Process 정보
        self.executionFunc = sys._getframe().f_code.co_name      # 실행 함수 이름
    
        # logstash 모듈 사용
        if self.category == "logstash":
            self.host = 'localhost'                                                             # logstash가 실행되는 주소
            self.logstash_Stream = logging.StreamHandler()                                      # log Console 창 출력을 위한 인스턴스
            self.logstash_handler = logstash.TCPLogstashHandler(self.host, port, version=1)     # log stash TCP 통신을 위한 인스턴스
            self.logstash_Logger = logging.getLogger('python-logstash-RPA')                     # logger 이름 지정
            self.logstash_Logger.addHandler(self.logstash_handler)                              # log stash 핸들러 추가
            self.logstash_Logger.addHandler(self.logstash_Stream)                               # Console의 log 출력용 핸들러 추가
            self.logstash_Logger.setLevel(logging.DEBUG)                                        # log level 설정

        # log 파일 사용
        elif self.category == "logfile":

            # log file 기본 경로 지정
            self.info_Logfile_Path = info_Path
            self.result_Logfile_Path = result_Path

            # file 핸들러 및 stream 핸들러 생성
            self.info_FileHandler = logging.FileHandler(self.info_Logfile_Path, encoding='utf-8', mode = 'a')    # log 파일 지정
            self.info_StreamHandler = logging.StreamHandler()                                       # log Console 창 출력을 위한 객체

            self.result_FileHandler = logging.FileHandler(self.result_Logfile_Path, encoding='utf-8', mode = 'a')  # log 파일 지정
            self.result_StreamHandler = logging.StreamHandler()                                     # log Console 창 출력을 위한 객체

            # logger 인스턴스 생성
            self.result_Logger = logging.getLogger("result-RPA")        # logger 이름 지정
            self.info_Logger = logging.getLogger("info-RPA")            # logger 이름 지정

            # log Format 지정
            self.info_logFileFormat = logging.Formatter("[%(levelname)s][%(time)s][%(host_name)s:%(clientip)s-%(os_name)s-%(os_version)s][%(proc_name)s:%(pid)d-%(execution_func)s:%(status)s] >> %(message)s")
            self.result_logFileFormat = logging.Formatter("[%(levelname)s][%(time)s][%(host_name)s:%(clientip)s-%(os_name)s-%(os_version)s][%(proc_name)s:%(pid)d-%(execution_func)s:%(status)s][%(file_path)s] >> %(message)s")

            # info log Handler 연결
            self.info_Logger.addHandler(self.info_FileHandler)               # log 파일에 log 연결
            self.info_Logger.addHandler(self.info_StreamHandler)              # Console에 log 연결

            # result log Handler 연결
            self.result_Logger.addHandler(self.result_FileHandler)            # log 파일에 log 연결
            self.result_Logger.addHandler(self.result_StreamHandler)          # Console에 log 연결

            # log file format 지정
            self.info_FileHandler.setFormatter(self.info_logFileFormat)        # log Format 셋팅
            self.info_StreamHandler.setFormatter(self.info_logFileFormat)       # log Format 셋팅

            self.result_FileHandler.setFormatter(self.result_logFileFormat)        # log Format 셋팅
            self.result_StreamHandler.setFormatter(self.result_logFileFormat)       # log Format 셋팅

            self.setLogfileSize()       # log file 사이즈 기본 값으로 변경

            # level = 특정 수준 이하의 모든 로그 메시지 출력 여부( DEBUG, INFO, WARNING, ERROR, CRITICAL)
            # 기본 log level 지정
            self.info_Logger.setLevel(logging.DEBUG)                                            # log level 설정
            self.result_Logger.setLevel(logging.DEBUG)                                          # log level 설정

        
        # logstash RPA 기본 정보 log 포맷
        self.info_Formatter = {
            "time" : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),      # 현재 시간
            "host_name" : socket.gethostname(),                                 # Hostname
            "clientip" : socket.gethostbyname(socket.gethostname()),            # 사용자의 IPv4 주소
            "os_name" : platform.system(),                                      # 사용자 OS
            "os_version" : platform.version(),                                  # 사용자 OS Version
            "proc_name" : self.proc.name,                                       # Process Name
            "pid" : self.proc.pid,                                              # Process ID
            "execution_func" : self.executionFunc,                              # 실행된 함수 이름
            "status" : "connect / disconnect / working / complete"              # RPA 프로그램 상태 (프로그램 실행 / 프로그램 종료 / 수행중 / 완료)
        }
        # RPA 결과물 log 포맷
        self.result_Formatter = {
            "time" : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),      # 현재 시간
            "host_name" : socket.gethostname(),                                 # Hostname
            "clientip" : socket.gethostbyname(socket.gethostname()),            # 사용자의 IPv4 주소
            "os_name" : platform.system(),                                      # 사용자 OS
            "os_version" : platform.version(),                                  # 사용자 OS Version
            "proc_name" : self.proc.name,                                       # Process Name
            "pid" : self.proc.pid,                                              # Process ID
            "execution_func" : self.executionFunc,                              # 실행된 함수 이름
            "status" : "complete",                                              # RPA 프로그램 상태 (완료)
            "file_path" : "RPA result file path"                                # 결과물 파일이 저장된 위치
        }

    # [INFO] log 전송 및 출력(info, result 타입 로그 지원, 기본값 info)
    def sendLog_InfoLevel(self, msg, formatter = "info"):

        self.info_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.result_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.info_Logger.info(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.result_Logger.info(msg, extra = self.result_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.logstash_Logger.info(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.logstash_Logger.info(msg, extra = self.result_Formatter)

    # [DEBUG] log 전송 및 출력(info, result 타입 로그 지원, 기본값 info)
    def sendLog_DebugLevel(self, msg, formatter = "info"):

        self.info_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.result_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.info_Logger.debug(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.result_Logger.debug(msg, extra = self.result_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.logstash_Logger.debug(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.logstash_Logger.debug(msg, extra = self.result_Formatter)
    
    # [WARNING] log 전송 및 출력(info, result 타입 로그 지원, 기본값 info)
    def sendLog_WarningLevel(self, msg, formatter = "info"):

        self.info_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.result_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.info_Logger.warning(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.result_Logger.warning(msg, extra = self.result_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.logstash_Logger.warning(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.logstash_Logger.warning(msg, extra = self.result_Formatter)

    # [ERROR] log 전송 및 출력(info, result 타입 로그 지원, 기본값 info)
    def sendLog_ErrorLevel(self, msg, formatter = "info"):

        self.info_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.result_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.info_Logger.error(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.result_Logger.error(msg, extra = self.result_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.logstash_Logger.error(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.logstash_Logger.error(msg, extra = self.result_Formatter)

    # [CRITICAL] log 전송 및 출력(info, result 타입 로그 지원, 기본값 info)
    def sendLog_CriticalLevel(self, msg, formatter = "info"):

        self.info_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.result_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.info_Logger.critical(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.result_Logger.critical(msg, extra = self.result_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "info":             # info formatter 형식 로그 전송
                self.logstash_Logger.critical(msg, extra = self.info_Formatter)
            elif formatter == "result":         # result formatter 형식 로그 전송
                self.logstash_Logger.critical(msg, extra = self.result_Formatter)
            
        
    # log File 저장 경로 변경
    def setLogfilePath(self, info_log, result_log):
        self.info_Logfile_Path = info_log
        self.result_Logfile_Path = result_log

        # 기존 핸들러 제거
        for handler in self.info_Logger.handlers[:]:
            self.info_Logger.removeHandler(handler)
        for handler in self.result_Logger.handlers[:]:
            self.result_Logger.removeHandler(handler)

        self.info_Logger.removeHandler(self.info_FileHandler)
        self.result_Logger.removeHandler(self.result_FileHandler)

        # file 핸들러 및 stream 핸들러 생성
        self.info_FileHandler = logging.FileHandler(self.info_Logfile_Path, encoding='utf-8')    # log 파일 지정
        self.info_StreamHandler = logging.StreamHandler()                                       # log Console 창 출력을 위한 객체
        self.result_FileHandler = logging.FileHandler(self.result_Logfile_Path, encoding='utf-8')  # log 파일 지정
        self.result_StreamHandler = logging.StreamHandler()                                     # log Console 창 출력을 위한 객체

        # info log Handler 연결
        self.info_Logger.addHandler(self.info_FileHandler)               # log 파일에 log 연결
        self.info_Logger.addHandler(self.info_StreamHandler)              # Console에 log 연결

        # result log Handler 연결
        self.result_Logger.addHandler(self.result_FileHandler)            # log 파일에 log 연결
        self.result_Logger.addHandler(self.result_StreamHandler)          # Console에 log 연결

        # log file format 지정
        self.info_FileHandler.setFormatter(self.info_logFileFormat)        # log Format 셋팅
        self.info_StreamHandler.setFormatter(self.info_logFileFormat)       # log Format 셋팅

        self.result_FileHandler.setFormatter(self.result_logFileFormat)        # log Format 셋팅
        self.result_StreamHandler.setFormatter(self.result_logFileFormat)       # log Format 셋팅

        self.setLogfileSize()       # log file 사이즈 기본 값으로 변경

        # 기본 log level 지정
        self.info_Logger.setLevel(logging.DEBUG)                                            # log level 설정
        self.result_Logger.setLevel(logging.DEBUG)                                          # log level 설정


    # log File 분할 사이즈 셋팅
    def setLogfileSize(self, fileMaxByte = 1024 * 1024 * 100, backupCount = 10):   # 파일 하나의 최대 바이트 수, log 파일 최대 개수
        
        self.info_FileHandler = logging.handlers.RotatingFileHandler(filename = self.info_Logfile_Path, maxBytes = fileMaxByte, backupCount = backupCount)  # 10개까지 log 파일을 남기겠다는 의미
        self.result_FileHandler = logging.handlers.RotatingFileHandler(filename = self.result_Logfile_Path, maxBytes = fileMaxByte, backupCount = backupCount)  # 10개까지 log 파일을 남기겠다는 의미
        

    # 실행된 함수 이름(execution_func), status 값 수정
    def setInfoFormat(self, funcName, status):
        self.info_Formatter["execution_func"] = funcName
        self.info_Formatter["status"] = status

    # 실행된 함수 이름(execution_func), status, file_path 수정
    def setResultFormat(self, funcName, file_path, status = "complete"):
        self.result_Formatter["execution_func"] = funcName
        self.result_Formatter["status"] = status
        self.result_Formatter["file_path"] = file_path
        

    # log level 설정(해당 level 이상 로그만 출력됨)
    def setLogLevel(self, level):
        if self.category == "logstash":
            self.logstash_Logger.setLevel(level)
        elif self.category == "logfile":
            self.info_Logger.setLevel(level)  # 해당 level 이상의 log만 출력
            self.result_Logger.setLevel(level)  # 해당 level 이상의 log만 출력

