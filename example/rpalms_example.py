from sk_optom import rpalms
import logging
import sys

def example(lms):
    # basic_Formatter의 포맷 수정(실행된 함수 이름(execution_func), status)
    lms.setBasicFormat(funcName=sys._getframe().f_code.co_name, status="working")

    # INFO Level 로그 전송
    lms.sendLog_InfoLevel("INFO Level Logging Test" , formatter = "basic")        # formatter 기본값은 basic 형식
    

if __name__ == "__main__" :

    ### logstash 모듈 방식 ###

    # 실행 함수 이름은 수시로 변경되기 때문에 따로 전달해야함
    executionFunc = sys._getframe().f_code.co_name         # 실행 함수 이름

    # logstash 모듈을 사용한 로그 전송을 위해 인스턴스 생성
    logstashTest = rpalms.RPA_LMS("logstash")

    # logstash 실행(.py 파일과 같은 디렉토리에 logstash가 위치해야함)
    logstashTest.run_Logstash()

    # INFO Level 로그 전송
    logstashTest.sendLog_InfoLevel("INFO Level Logging Test")        # formatter 기본값은 basic 형식

    # 전송하고자 하는 로그 레벨 지정
    logstashTest.setLogLevel(logging.DEBUG)
    
    # extend_Formatter의 포맷 수정(실행된 함수 이름(execution_func), status, file_path)
    logstashTest.setExtendFormat(funcName=executionFunc, file_path="C:/test", status="complete")

    # basic_Formatter의 포맷 수정(실행된 함수 이름(execution_func), status)
    logstashTest.setBasicFormat(funcName=executionFunc, status="working")

    example(logstashTest)

    ### Log Level 별로 전송, level( DEBUG, INFO, WARNING, ERROR, CRITICAL)
    ### (formatter 매개변수 - basic, extend 타입 로그 지원, 기본값 basic)
    logstashTest.sendLog_InfoLevel("1", formatter="basic")
    logstashTest.sendLog_DebugLevel("2", formatter="extend")
    logstashTest.sendLog_ErrorLevel("3")
    logstashTest.sendLog_CriticalLevel("4")
    logstashTest.sendLog_WarningLevel("5")
    
    ###############################################################################################################
    
    ### log file 방식 ###

    # logfile을 사용한 로그 전송을 위해 인스턴스 생성(log file 경로 지정안하면 기본 값 사용)
    logfileTest = rpalms.RPA_LMS("logfile", basic_Path=r"./log/basic.log", extend_Path=r"./log/extend.log")

    # logfile 저장 경로 변경 (basic_log= basic log 저장경로, extend_log= extend log 저장경로)
    logfileTest.setLogfilePath(basic_log = r"./log/your_path1.log", extend_log = r"./log/your_path2.log")

    # logfile 용량 및 개수 설정
    logfileTest.setLogfileSize(fileMaxByte=1024 * 1024 * 100, backupCount = 10)    # 파일 하나의 최대 바이트 수

    example(logfileTest)
    
    ### Log Level 별로 전송, level( DEBUG, INFO, WARNING, ERROR, CRITICAL)
    ### (formatter 매개변수 - basic, extend 타입 로그 지원, 기본값 basic)
    logfileTest.sendLog_InfoLevel("1", formatter="basic")
    logfileTest.sendLog_DebugLevel("2", formatter="extend")
    logfileTest.sendLog_ErrorLevel("3")
    logfileTest.sendLog_CriticalLevel("4")
    logfileTest.sendLog_WarningLevel("5")
