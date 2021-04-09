import logging
import logstash
import sys
import socket
import platform
import psutil
import multiprocessing as mp
import time
import os

# RPA LMS 로그 관리 모듈
class RPA_LMS:
    def __init__(self, category, port = 5900, basic_Path = r"./log/basic.log", extend_Path = r"./log/extend.log"):   # category는 logfile(.log 파일), logstash(python-logstash 모듈) 2가지 지원

        self.category = category
        self.proc = mp.current_process()                        # 현재 Process 정보
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
            self.basic_Logfile_Path = basic_Path
            self.extend_Logfile_Path = extend_Path

            # log 파일 저장될 디렉토리 생성
            path = os.getcwd() + "\\log"
            os.makedirs(path, exist_ok = True)

            # file 핸들러 및 stream 핸들러 생성
            self.basic_FileHandler = logging.FileHandler(self.basic_Logfile_Path, encoding='utf-8', mode = 'a')    # log 파일 지정
            self.basic_StreamHandler = logging.StreamHandler()                                       # log Console 창 출력을 위한 객체

            self.extend_FileHandler = logging.FileHandler(self.extend_Logfile_Path, encoding='utf-8', mode = 'a')  # log 파일 지정
            self.extend_StreamHandler = logging.StreamHandler()                                     # log Console 창 출력을 위한 객체

            # logger 인스턴스 생성
            self.extend_Logger = logging.getLogger("extend-RPA")        # logger 이름 지정
            self.basic_Logger = logging.getLogger("basic-RPA")            # logger 이름 지정

            # log Format 지정
            self.basic_logFileFormat = logging.Formatter("[%(levelname)s][%(time)s][%(host_name)s:%(clientip)s-%(os_name)s-%(os_version)s][%(proc_name)s:%(pid)d-%(execution_func)s:%(status)s] >> %(message)s")
            self.extend_logFileFormat = logging.Formatter("[%(levelname)s][%(time)s][%(host_name)s:%(clientip)s-%(os_name)s-%(os_version)s][%(proc_name)s:%(pid)d-%(execution_func)s:%(status)s][%(file_path)s] >> %(message)s")

            # basic log Handler 연결
            self.basic_Logger.addHandler(self.basic_FileHandler)               # log 파일에 log 연결
            self.basic_Logger.addHandler(self.basic_StreamHandler)              # Console에 log 연결

            # extend log Handler 연결
            self.extend_Logger.addHandler(self.extend_FileHandler)            # log 파일에 log 연결
            self.extend_Logger.addHandler(self.extend_StreamHandler)          # Console에 log 연결

            # log file format 지정
            self.basic_FileHandler.setFormatter(self.basic_logFileFormat)        # log Format 셋팅
            self.basic_StreamHandler.setFormatter(self.basic_logFileFormat)       # log Format 셋팅

            self.extend_FileHandler.setFormatter(self.extend_logFileFormat)        # log Format 셋팅
            self.extend_StreamHandler.setFormatter(self.extend_logFileFormat)       # log Format 셋팅

            self.setLogfileSize()       # log file 사이즈 기본 값으로 변경

            # level = 특정 수준 이하의 모든 로그 메시지 출력 여부( DEBUG, INFO, WARNING, ERROR, CRITICAL)
            # 기본 log level 지정
            self.basic_Logger.setLevel(logging.DEBUG)                                            # log level 설정
            self.extend_Logger.setLevel(logging.DEBUG)                                          # log level 설정

        
        # logstash RPA 기본 정보 log 포맷
        self.basic_Formatter = {
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
        self.extend_Formatter = {
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

    # [INFO] log 전송 및 출력(basic, extend 타입 로그 지원, 기본값 basic)
    def sendLog_InfoLevel(self, msg, formatter = "basic"):

        self.basic_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.extend_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.basic_Logger.info(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.extend_Logger.info(msg, extra = self.extend_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.logstash_Logger.info(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.logstash_Logger.info(msg, extra = self.extend_Formatter)

    # [DEBUG] log 전송 및 출력(basic, extend 타입 로그 지원, 기본값 basic)
    def sendLog_DebugLevel(self, msg, formatter = "basic"):

        self.basic_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.extend_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.basic_Logger.debug(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.extend_Logger.debug(msg, extra = self.extend_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.logstash_Logger.debug(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.logstash_Logger.debug(msg, extra = self.extend_Formatter)
    
    # [WARNING] log 전송 및 출력(basic, extend 타입 로그 지원, 기본값 basic)
    def sendLog_WarningLevel(self, msg, formatter = "basic"):

        self.basic_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.extend_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.basic_Logger.warning(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.extend_Logger.warning(msg, extra = self.extend_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.logstash_Logger.warning(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.logstash_Logger.warning(msg, extra = self.extend_Formatter)

    # [ERROR] log 전송 및 출력(basic, extend 타입 로그 지원, 기본값 basic)
    def sendLog_ErrorLevel(self, msg, formatter = "basic"):

        self.basic_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.extend_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.basic_Logger.error(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.extend_Logger.error(msg, extra = self.extend_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.logstash_Logger.error(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.logstash_Logger.error(msg, extra = self.extend_Formatter)

    # [CRITICAL] log 전송 및 출력(basic, extend 타입 로그 지원, 기본값 basic)
    def sendLog_CriticalLevel(self, msg, formatter = "basic"):

        self.basic_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())      # 시간 업데이트
        self.extend_Formatter["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())    # 시간 업데이트

        # logfile 사용
        if self.category == "logfile":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.basic_Logger.critical(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.extend_Logger.critical(msg, extra = self.extend_Formatter)

        # logstash 모듈 사용
        elif self.category == "logstash":

            if formatter == "basic":             # basic formatter 형식 로그 전송
                self.logstash_Logger.critical(msg, extra = self.basic_Formatter)
            elif formatter == "extend":         # extend formatter 형식 로그 전송
                self.logstash_Logger.critical(msg, extra = self.extend_Formatter)
            
        
    # log File 저장 경로 변경
    def setLogfilePath(self, basic_log, extend_log):
        self.basic_Logfile_Path = basic_log
        self.extend_Logfile_Path = extend_log

        # 기존 핸들러 제거
        for handler in self.basic_Logger.handlers[:]:
            self.basic_Logger.removeHandler(handler)
        for handler in self.extend_Logger.handlers[:]:
            self.extend_Logger.removeHandler(handler)

        self.basic_Logger.removeHandler(self.basic_FileHandler)
        self.extend_Logger.removeHandler(self.extend_FileHandler)

        # file 핸들러 및 stream 핸들러 생성
        self.basic_FileHandler = logging.FileHandler(self.basic_Logfile_Path, encoding='utf-8')    # log 파일 지정
        self.basic_StreamHandler = logging.StreamHandler()                                       # log Console 창 출력을 위한 객체
        self.extend_FileHandler = logging.FileHandler(self.extend_Logfile_Path, encoding='utf-8')  # log 파일 지정
        self.extend_StreamHandler = logging.StreamHandler()                                     # log Console 창 출력을 위한 객체

        # basic log Handler 연결
        self.basic_Logger.addHandler(self.basic_FileHandler)               # log 파일에 log 연결
        self.basic_Logger.addHandler(self.basic_StreamHandler)              # Console에 log 연결

        # extend log Handler 연결
        self.extend_Logger.addHandler(self.extend_FileHandler)            # log 파일에 log 연결
        self.extend_Logger.addHandler(self.extend_StreamHandler)          # Console에 log 연결

        # log file format 지정
        self.basic_FileHandler.setFormatter(self.basic_logFileFormat)        # log Format 셋팅
        self.basic_StreamHandler.setFormatter(self.basic_logFileFormat)       # log Format 셋팅

        self.extend_FileHandler.setFormatter(self.extend_logFileFormat)        # log Format 셋팅
        self.extend_StreamHandler.setFormatter(self.extend_logFileFormat)       # log Format 셋팅

        self.setLogfileSize()       # log file 사이즈 기본 값으로 변경

        # 기본 log level 지정
        self.basic_Logger.setLevel(logging.DEBUG)                                            # log level 설정
        self.extend_Logger.setLevel(logging.DEBUG)                                          # log level 설정


    # logstash 실행(.py 파일과 같은 디렉토리에 logstash가 위치해야함)
    def run_Logstash(self, batchFile = "run_lms.bat"):
        curDir = os.getcwd()
        logstash_Dir = curDir + "\\logstash\\bin"
        logstash = logstash_Dir + "\\" + batchFile
        os.chdir(logstash_Dir)
        os.startfile(logstash)


    # log File 분할 사이즈 셋팅
    def setLogfileSize(self, fileMaxByte = 1024 * 1024 * 100, backupCount = 10):   # 파일 하나의 최대 바이트 수, log 파일 최대 개수
        
        self.basic_FileHandler = logging.handlers.RotatingFileHandler(filename = self.basic_Logfile_Path, maxBytes = fileMaxByte, backupCount = backupCount)  # 10개까지 log 파일을 남기겠다는 의미
        self.extend_FileHandler = logging.handlers.RotatingFileHandler(filename = self.extend_Logfile_Path, maxBytes = fileMaxByte, backupCount = backupCount)  # 10개까지 log 파일을 남기겠다는 의미
        

    # 실행된 함수 이름(execution_func), status 값 수정
    def setBasicFormat(self, funcName, status):
        self.basic_Formatter["execution_func"] = funcName
        self.basic_Formatter["status"] = status

    # 실행된 함수 이름(execution_func), status, file_path 수정
    def setExtendFormat(self, funcName, file_path, status = "complete"):
        self.extend_Formatter["execution_func"] = funcName
        self.extend_Formatter["status"] = status
        self.extend_Formatter["file_path"] = file_path
        

    # log level 설정(해당 level 이상 로그만 출력됨)
    def setLogLevel(self, level):
        if self.category == "logstash":
            self.logstash_Logger.setLevel(level)
        elif self.category == "logfile":
            self.basic_Logger.setLevel(level)  # 해당 level 이상의 log만 출력
            self.extend_Logger.setLevel(level)  # 해당 level 이상의 log만 출력

