---
sidebar_position: 1
id: IMXNET 설치 가이드
title: IMXNET 설치 가이드
---

# 1. IMXNET 설치 전 사전 준비
- 모니터링 할 수집서버와 Agent에 대한 해당 Port를 Open

| 출발지 | Port | Protocol | 목적지 | 설명 |
| :-: | :-: | :-: | :-: | :-: |
| IMXTXN | 1314 | TCP | DG | SQL관련 정보 전송 |
| IMXOSM | 1314 | TCP | DG | OS 리소스 정보 전송 |
| \.NET Agent | 1314 | TCP | DG | \.NET Agent 수집내용 전송 |
| PC\(PJS\) | 8082 | TCP | DG | 클라이언트 접속 |

- V5\.3 2022\.08 이후 버전
    중앙라이센스 필수
    트랜잭션 수집 X

# 2. IMXNET 설치

  1) 해당 압축 파일을 아래에 경로에 압축 해제
    InterMax\_DoNet\_2106\.02.zip
    ![](img%5CDotnet_0.png)

  2) intermax 하위의 <span style="color:#ff0000">dotnet</span>  디렉토리명 변경 불가
    권한문제 피하기 위해 가급적 최상위 폴더를 사용
    Ex) C:/intermax, D:/intermax

# 3. 설치 파일 별 용도

1) C:\\intermax\\dotnet\\tools

2) C:\\intermax\\dotnet\\tools\\Assembly :  어셈블리 설치
설치 경로는 C:\\Windows\\assembly\\ 또는

3) C:\\Windows\\Microsoft\.NET\\assembly\\GAC\_MSIL\\InterMax\.NetAgent에 dll 파일 배포
패치 및 설치 점검시 해당경로에 파일을 확인한다\.

4) C:\\intermax\\dotnet\\tools\\dll\_regsvr
Dll 파일 레지스트리에 등록  regedit 열어서 아래 항목 확인

5) 컴퓨터\\HKEY\_CLASSES\_ROOT\\CLSID\\\{3F752343\-A1EA\-4078\-B6A9\-A280CE5A5E0B\}\\InprocServer32

6) C:\\intermax\\dotnet\\binary\\Intermax\.Profiler\.x64\.dll

7) C:\\intermax\\dotnet\\tools\\Oracle
오라클 커넥션 모니터링에 사용

8) C:\\intermax\\dotnet\\tools\\OsmService
osm 서비스 등록시 사용

9) C:\\intermax\\dotnet\\tools\\Visual Studio 2017 C\+\+ Redistributable

10) 닷넷 모니터링위한 라이브러리 설치파일
profile\_for\_service\_start\.bat
profile\_for\_service\_stop\.bat

11) W3WP \, WAS 레지스트리 값 추가 / 삭제
UnInstall\.bat
osm \, vc 를 제외한 설치항목 삭제

12) C:\\intermax\\dotnet\\config
net\.conf 	:에이전트 옵션 jspd\.prop\.ini 와 같은 용도
net\.home 	:jspd\.home 과 같은용도 동적적용시
net\.priority\.txn	:PLC 설정시 사용
net\.wasid	:wasid 설정에 사용 iis 가상디렉토리마다 설정
profile\.advice	:콜트리 설정 \( jspd\.local\.advice \, x\.advice \, other\.advice  \)
profile\.callback\.conf	:콜트리 정의 \( 변경 불필요 \)
service\.target	:profile\_for\_service\_start\.bat 파일에서 레지스트리 설정할 서비스목록 작성

13) C:\\intermax\\dotnet\\lib\\
imx 라이브러리 파일

14) C:\\intermax\\dotnet\\cfg\\agent
Imxosm \, imxtxn 동작을 위한 파일
jspd.prop 설치시 WR_ADDR=10\.31\.253\.116:1314 설정

15) C:\\intermax\\dotnet\\binary
GUI 설치 툴 및 dll 바이너리 파일 dll 패치시 이 경로에 변경

__2\. __  __DotNet__  __ Agent __  __설치 __  __\( IIS__  __ __  __\)__  __ __

내pc에서 우클릭 후  속성 Properties를 선택

![](img%5CDotnet_1.png)

![](img%5CDotnet_2.png)

고급설정\(Advanced system settings\)에서

환경 변수\(Environment Variables\) 선택

__2\. __  __DotNet__  __ Agent __  __설치 __  __\( IIS__  __ __  __\)__  __ __

시스템 변수\(System variables\)에 환경변수 추가

![](img%5CDotnet_3.png)

__INTERMAX\_PATH __  __환경변수 추가__

![](img%5CDotnet_4.png)

C:\\intermax <span style="color:#ff0000">\\</span>

<span style="color:#ff0000">끝에 </span>  <span style="color:#ff0000">\\ </span>  <span style="color:#ff0000">붙는경우</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">osm</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">비정상 동작 </span>  <span style="color:#ff0000">할수</span>  <span style="color:#ff0000"> 있으니 주의 </span>

__INTERMAX\_PROFILE\_TARGET\_PROCESS __  __환경 변수 추가__

![](img%5CDotnet_5.png)

__2\. __  __DotNet__  __ Agent __  __설치 __  __\( IIS__  __ __  __\)__  __ __

vc\_redist 파일 두개 모두 설치\( <span style="color:#ff0000">Intermax</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">삭제시에도</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">uninstall </span>  <span style="color:#ff0000">금지</span> \)

경로: C:\\intermax\\dotnet\\tools\\

Visual Studio 2017 C\+\+ Redistributable\\vc\_redist\.x64\.exe\, vc\_redist\.x86\.exe

![](img%5CDotnet_6.png)

vc\_redist\.x64\, vc\_redist\.x86 모두 설치

세개의 파일 실행 하여 모두 설치\( <span style="color:#ff0000">환경변수  사전에 반드시 확인</span> \)

경로: C:\\intermax\\dotnet\\tools\\Assembly\\assembly\_regist\.bat

\(C:\\windows\\assembly 에 dll파일배포 \)

경로: C:\\intermax\\dotnet\\tools\\dll\_regsvr\\DLL\_Install\.bat

\(레지스트리에 DLL 파일 등록  \)

경로: C:\\intermax\\dotnet\\tools\\profile\_for\_service\_start\.bat

\( IIS 에 profiler 적용   \)

![](img%5CDotnet_7.png)

![](img%5CDotnet_8.png)

![](img%5CDotnet_9.png)

<span style="color:#ff0000">CMD</span>  <span style="color:#ff0000">는 관리자 권한으로 실행 </span>

__2\. __  __DotNet__  __ Agent __  __설치 __  __\( IIS__  __ __  __\)__  __ __

![](img%5CDotnet_10.png)

경로: C:\\intermax\\dotnet\\cfg\\agent\\jspd\.prop

jspd\.prop파일 수정하여 수집서버 IP와 Port를 기입 후 저장

![](img%5CDotnet_11.png)

경로: C:\\intermax\\dotnet\\config\\net\.conf

net\.conf파일 수정하여 수집서버 IP와 Port를 기입 후 저장

![](img%5CDotnet_12.png)

![](img%5CDotnet_13.png)

__2\. __  __DotNet__  __ Agent __  __설치 __  __\( IIS__  __ __  __\)__  __ __

intermax\.config\.util\.exe 툴 사용 방법

경로: C:\\intermax\\dotnet\\binary

![](img%5CDotnet_14.png)

![](img%5CDotnet_15.png)

intermax\.config\.util\.exe를 실행

실행후 Enable profile 선택 그리고 WAS ID 를 입력\, 저장

해당 바이너리 실행 안되는경우

2\)  net\.wasid 파일 직접 수정 방법 으로 설정

__2\. __  __DotNet__  __ Agent __  __설치 __  __\( IIS__  __ __  __\)__  __ __

2\)  net\.wasid 파일 직접 수정 방법

경로: C:\\intermax\\dotnet\\config

![](img%5CDotnet_16.png)

<span style="color:#ff0000">오타 주의 </span> 직접입력시 아래 명령어로 확인하여 진행

appcmd\.exe list app /site\.name=“test2”

![](img%5CDotnet_17.png)

![](img%5CDotnet_18.png)

__2\. __  __DotNet__  __ Agent __  __설치  __  __\( IIS__  __ __  __\)__  __ __

경로: C:\\intermax\\dotnet\\lib\\imx

![](img%5CDotnet_19.png)

![](img%5CDotnet_20.png)

작업관리자에서 intermax 실행 확인

![](img%5CDotnet_21.png)

<span style="color:#ff0000">최초 </span>  <span style="color:#ff0000">lib\\IMXOSM\_SA\.bat</span>  <span style="color:#ff0000"> 파일 실행 하고 </span> 로그 파일 생긴후 프로세스 죽이고 서비스로 기동

__2\. __  __DotNet__  __ Agent __  __설치  __  __\( IIS__  __ __  __\)__  __ __

컴퓨터\\HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\W3SVC

![](img%5CDotnet_22.png)

에이전트  <span style="color:#ff0000">임시 설치 </span>  <span style="color:#ff0000">제거시</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">해당값</span>  <span style="color:#ff0000"> 삭제 </span>

또는 tools/profile\_for\_service\_stop\.bat 실행

__2\. __  __DotNet__  __ Agent __  __설치  __  __\( IIS__  __ __  __\)__  __ __

![](img%5CDotnet_23.png)

<span style="color:#ff0000">정상설치된</span>  <span style="color:#ff0000"> 경우 </span>  <span style="color:#ff0000">Process Explorer \(</span>  <span style="color:#ff0000">별도다운로드</span>  <span style="color:#ff0000">\)</span>  <span style="color:#ff0000">에서 </span>

<span style="color:#ff0000">Intermax\.NetAgent\.dll \, Intermax\.Profiler\.x64\.dll </span>

<span style="color:#ff0000">파일이 로드 </span>

![](img%5CDotnet_24.png)

![](img%5CDotnet_25.png)

<span style="color:#ff0000">W3wp\.exe </span>  <span style="color:#ff0000">프로세스의 </span>

<span style="color:#ff0000">Properties </span>  <span style="color:#ff0000">의 </span>  <span style="color:#ff0000">Environment </span>

<span style="color:#ff0000">항목에서 </span>  <span style="color:#ff0000">3F752343…\. </span>  <span style="color:#ff0000">을 </span>

<span style="color:#ff0000">확인</span>

<span style="color:#ff0000">3F75\.\.</span>  <span style="color:#ff0000">가 아닌 </span>

<span style="color:#ff0000">다른값인</span>  <span style="color:#ff0000"> 경우 타사 </span>

<span style="color:#ff0000">모니터링</span>  <span style="color:#ff0000">tool</span>  <span style="color:#ff0000">에서 </span>

<span style="color:#ff0000">적용된 옵션 </span>

__2\. __  __DotNet__  __ Agent __  __설치  __  __\( IIS__  __ __  __\)__  __ __

앞에 설치 과정중 Vc 설치과정을 제외한

assembly \, DLL\_install  \, imxosm 서비스등록 IIS Restry 등록을 자동화한

install\.bat 파일   반드시 intermax/ <span style="color:#ff0000">dotnet/tools/</span>   <span style="color:#ff0000">경로에서 관리자권한으로 실행한다</span>  <span style="color:#ff0000">\.</span>

![](img%5CDotnet_26.png)

![](img%5CDotnet_27.png)

![](img%5CDotnet_28.png)

__3\. __  __수집서버에서 __  __Agent __  __추가설정 및 확인 __

![](img%5CDotnet_29.png)

수집서버 RTM 에서 환경설정 메뉴 클릭

에이전트 설정 선택 시 설정한 Agent가 에이전트 ID만 기입 된 상태로 표시

\+ 버튼으로 에이전트 이름과 호스트명을 기입 하고 저장

서비스 설정에 들어가 추가한 에이전트를 원하는 서비스에 추가

![](img%5CDotnet_30.png)

__3\. __  __수집서버에서 __  __Agent __  __추가설정 및 확인 __

![](img%5CDotnet_31.png)

추가된 Agent\(DotNet\)의 트랜잭션 및 cpu\,memory등을 확인

![](img%5CDotnet_32.png)

__4\. __  __Intermax__  __ __  __삭제 방법__  __\(Uninstall\)__

C:\\intermax\\dotnet\\tools\\uninstall\.bat 파일 관리자 권한으로 실행

![](img%5CDotnet_33.png)

<span style="color:#ff0000">Visual Studio 2017 C\+\+ Redistributable</span>

<span style="color:#ff0000">삭제 금지 </span>

C:\\intermax\\dotnet\\tools\\OsmService\\uninstall\_osm\_service\.bat

__5\. __  __DotNet__  __ Agent\(IIS\) __  __설치 전체 순서 요약__

__설치파일 __  __Dotnet Agent __  __서버로 전송__

설치 파일명: InterMax\_DotNet\_2106\.02\.zip

__설치파일 압축해제__

__     __ InterMax\_DotNet\_2106\.02\.zip의 해제 경로: C:\\intermax

__Visual studio __  __설치__

__     __ 경로 : C:\\intermax\\dotnet\\tools\\Visual Studio 2017 C\+\+ Redistributable

__     __ 설치파일 : vc\_redist\.x64\.exe\, vc\_redist\.x86\.exe \(둘다 설치\)

__4\)  __  __환경변수 설정 __

변수이름: INTERMAX\_PATH              변수이름: INTERMAX\_PROFILE\_TARGET\_PROCESS

변수 값  : C:\\intermax                    변수 값 : w3wp\.exe

__5\. __  __DotNet__  __ Agent\(IIS\) __  __설치 전체 순서 요약__

__5\)  __  __각 __  __dll__  __ __  __파일 실행하여 설치 __  __\(__  __세개의 파일__  __\)__

설치 파일명:

C:\\intermax\\dotnet\\tools\\Assembly\\assembly\_regist\.bat

C:\\intermax\\dotnet\\tools\\dll\_regsvr\\DLL\_Install\.bat

C:\\intermax\\dotnet\\tools\\profile\_for\_service\_start\.bat

__6\)  WAS ID __  __등록__

C:\\intermax\\dotnet\\binary 폴더에 있는 intermax\.config\.util\.exe 실행 파일을 사용

__수집 서버 __  __IP __  __및 __  __Port __  __등록__  __ \(__  __둘다 수정 후__  __ __  __저장__  __\)__

경로: C:\\intermax\\dotnet\\cfg\\agent\\jspd\.prop

경로: C:\\intermax\\dotnet\\config\\net\.conf

__5\. __  __DotNet__  __ Agent\(IIS\) __  __설치 전체 순서 요약__

__8\) IMXOSM __  __서비스 등록__

__    __  경로: C:\\intermax\\dotnet\\tools\\OsmService\\install\_osm\_service\.bat

__IMXOSM __  __실행__

__     __ 경로: C:\\intermax\\dotnet\\lib

__     __ 파일: IMXOSM\_SA\.bat \(실행\)

__10\) IIS __  __재기동__  __ 후 수집 서버에서 확인__

__      __  __iisreset__  __ __

__6\.1 __  __DotNet__  __ \( __  _Service_  __ \) Agent __  __설치__

__6\.2 __  __DotNet__  __ \( EXE__  __ __  __\) Agent __  __설치__

__6\.1 __  __DotNet__  __ \( __  _Service_  __ \) Agent __  __설치__

설치파일 업로드 InterMax\_DotNet\_2106\.02\.zip 및 압축해제

![](img%5CDotnet_34.png)

2\. 윈도우 환경 변수 등록

INTERMAX\_PATH=D:\\intermax

<span style="color:#ff0000">       INTERMAX\_PROFILE\_TARGET\_PROCESS=</span>  <span style="color:#ff0000">서비스프로세스명</span>

![](img%5CDotnet_35.png)

__6\.1 __  __DotNet__  __ \( __  _Service_  __ \) Agent __  __설치__

라이브러리 설치 \(IIS 와 동일\)

재배포 패키지  \, OSM 서비스 설치

![](img%5CDotnet_36.png)

![](img%5CDotnet_37.png)

Assembly \, DLL 설치

![](img%5CDotnet_38.png)

![](img%5CDotnet_39.png)

__6\.1 __  __DotNet__  __ \( __  _Service_  __ \) Agent __  __설치__

<span style="color:#ff0000">Service\.target</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">파일 수정 </span>  <span style="color:#ff0000"> </span>

<span style="color:#ff0000">서비스 목록에 있는 이름으로 추가  </span>

![](img%5CDotnet_40.png)

<span style="color:#ff0000">net\.wasid</span>  <span style="color:#ff0000"> 파일 수정</span>

<span style="color:#ff0000">service:실행서비스명\,서비스파일실행exe명</span>  <span style="color:#ff0000">=\{</span>  <span style="color:#ff0000">wasid</span>  <span style="color:#ff0000">\}</span>

service:exemDemoService\,exemdemo\.service\.exe=100

![](img%5CDotnet_41.png)

__6\.1 __  __DotNet__  __ \( __  _Service_  __ \) Agent __  __설치__

컴퓨터\\HKEY\_LOCAL\_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\

하위에서 모니터링 하고자 하는 서비스에 아래와 같이 레지스트리 값 추가

Name : Environment

Data  : cor\_enable\_profiling=0x1

cor\_profiler=\{3F752343\-A1EA\-4078\-B6A9\-A280CE5A5E0B\}

![](img%5CDotnet_42.jpg)

<span style="color:#ff0000">Service\.target</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">파일 수정 후 </span>  <span style="color:#ff0000">profile\_for\_service\_start\.bat </span>  <span style="color:#ff0000">실행시</span>  <span style="color:#ff0000"> 적용됨</span>

__6\.2 __  __DotNet__  __ \( EXE__  __ __  __\) Agent __  __설치__

\(1\) 시스템 환경변수 INTERMAX\_PROFILE\_TARGET\_PROCESS 옵션에  w3wp\.exe 대신 exe 실행파일명을 적어줌\.

![](img%5CDotnet_43.png)

\(2\) oov\.server\.exe 만 실행하는 닷넷 프로세스에 에이전트 설치시

bat 파일을 하나 만들어  <span style="color:#ff0000">해당 </span>  <span style="color:#ff0000">bat </span>  <span style="color:#ff0000">파일을 통해서 실행함</span>

![](img%5CDotnet_44.png)

__6\.2 __  __DotNet__  __ \( EXE__  __ __  __\) Agent __  __설치__

\(3\) Wasid 파일에는 아래와 같이 application:\[exe파일명\]=id값 으로 설정해준다

![](img%5CDotnet_45.png)

\(4\) imx\.conf에 아래와 같이 실행되는 exe 파일명을 적어준다\.

WAS\_PROCESS\_NAME=OneClick\.Server

\(5\) 그 외 콜트리 및 기타 설정은 IIS \, Service 와 동일함

<span style="color:#ff0000">\(6\) http request</span>  <span style="color:#ff0000"> 가 아닌 경우에는 시작점이 필요함</span>  <span style="color:#ff0000">\. </span>

__7\. __  __권장 변경 옵션  __

\(1\)net\.conf 변경

콜트리 CURR\_TRACE\_TXN=\*:1000 \(기본값 0 \)

바인드 수집 BIND\_ELAPSE\_TIME=1000 \(기본값 0 \)

\(2\)imx\.prop

SQL\_DETAIL\_ELAPSE\_LIMIT=100 \(net\.conf 에서도가능 기본값 0\)

부하 상황에 따라 고객과 협의 필요

__8\. __  __트러블 슈팅 __

__0\) __  __vc__  __ __  __재배포__  __ 패키지 설치 오류 __  __/ Assembly __  __설치 오류  __

상위버전이 설치되어 있어 설치를 할 수 없는 경우

<span style="color:#ff0000">시스템에 있는 상위버전을 설치 제거하면 </span>

<span style="color:#ff0000">업무에 문제가 </span>  <span style="color:#ff0000">발생할수</span>  <span style="color:#ff0000"> 있음  </span>

재배포 패키지는 삭제 하지말 것

상위 버전이 있는 경우 Skip하고 다음 Step으로 진행

![](img%5CDotnet_46.png)

경로: C:\\intermax\\dotnet\\tools\\Assembly\\assembly\_regist\.bat

<span style="color:#ff0000">failure</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">initializing</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">gacutil</span>  <span style="color:#ff0000"> </span> 발생시

Power shell 열어서 아래와 같이 입력 \(줄바꿈 shift \+ enter\)

![](img%5CDotnet_47.png)

\[System\.Reflection\.Assembly\]::LoadWithPartialName\("System\.EnterpriseServices"\) | Out\-Null

$publish = New\-Object System\.EnterpriseServices\.Internal\.Publish

$InterMaxPath = Join\-Path $env:INTERMAX\_PATH "\\dotnet\\binary\\4\.0\\InterMax\.NetAgent\.dll"

$publish\.GacInstall\($InterMaxPath\)

\[System\.Reflection\.Assembly\]::LoadWithPartialName\("System\.EnterpriseServices"\) | Out\-Null

$publish = New\-Object System\.EnterpriseServices\.Internal\.Publish

$InterMaxPath = Join\-Path $env:INTERMAX\_PATH "\\dotnet\\binary\\4\.0\\log4net\.dll"

$publish\.GacInstall\($InterMaxPath\)

<span style="color:#333333">C:\\</span>  <span style="color:#333333">Windows\\</span>  <span style="color:#438fff">[Microsoft\.NET](http://microsoft.net/)</span>  <span style="color:#333333">\\assembly\\GAC\_MSIL </span>  <span style="color:#333333">에 </span>  <span style="color:#333333">InterMax\.NetAgent</span>  <span style="color:#333333"> </span>

<span style="color:#333333">log4net </span>  <span style="color:#333333">설치 확인 </span>

__8\. __  __트러블 슈팅 __

assembly\_regit\.bat \, DLL\_Install\.bat 실행 시 아래와 같이 발생

![](img%5CDotnet_48.png)

![](img%5CDotnet_49.png)

환경변수를 INTERMAX\_PATH를 지정하지 않아 특정 파일을 찾을 수 없음

__8\. __  __트러블 슈팅 __

assembly\_regit\.bat\,profile\_for\_service\_start 파일등도 환경변수를 따름

![](img%5CDotnet_50.png)

InterMax\.NetAgent\.dll을 찾을 수 없어 설치 자체가 불가

Profile\_for\_service\_start파일도 환경변수 미설정 시 찾지를 못함

__8\. __  __트러블 슈팅 __

__2\) __  __설치 검증 방법__  __ __  __ __  __\- assembly __  __버전 확인 방법__

C:\\intermax\\dotnet\\tools\\Assembly\\\_assembly\_view

![](img%5CDotnet_51.png)

\_assembly\_view\.bat을 이용하여 install info를 확인

__8\. __  __트러블 슈팅 __

__2\) __  __설치 검증 방법__  __ \- assembly __  __버전 확인 방법__

![](img%5CDotnet_52.png)

![](img%5CDotnet_53.png)

실제 dll 배포 경로에 가서 확인

__8\. __  __트러블 슈팅 __

__2\) __  __설치 검증 방법__  __ – DLL\_Install\.bat __

![](img%5CDotnet_54.png)

![](img%5CDotnet_55.png)

Ctrl \+ F 로 intermax 찾아서 해당위치에 값 확인

__8\. __  __트러블 슈팅 __

__2\) __  __설치 검증 방법__  __ – profile\_for\_service\_start\.bat__

![](img%5CDotnet_56.png)

실제 dll 배포 경로에 가서 확인

__8\. __  __트러블 슈팅 __

__3\) Process Explorer__  __로 __  __dll__  __ __  __모듈 및 __  __COR\_PROFILER __  __찾는 방법__

__Process Explorer __  __관리자 권한 실행하여 __  __w3wp\.exe __  __프로세스에 __  __dll__  __ __  __목록에 __  __intermax\.NetAgent\.dll __  __확인   __

![](img%5CDotnet_57.png)

__8\. __  __트러블 슈팅 __

__3\) Process Explorer__  __로 __  __dll__  __ __  __모듈 및 __  __COR\_PROFILER __  __찾는 방법__

__w3wp\.exe __  __프로세스에 __  __우클릭__  __ 하여 __  __properties__  __에서 __  __Environment __  __에서 __

__Cor\_profiler__  __ __  __에 __  __인터맥스__  __ 값 __  __\{3F75 …\.\.\} __  __값 확인 __

![](img%5CDotnet_58.png)

![](img%5CDotnet_59.png)

__8\. __  __트러블 슈팅 __

__4\) __  __타사 __  __APM __  __및 기타 솔루션으로 인해 __  __COR\_PROFILER __  __사용시 대응 방법__

레지스트리에 값이 잘들어가 있음에도 불구하고 Process Explorer 에서 확인해보면

Cor\_profiler 값이 타사 제품의 값으로 들어가 있음

타사 제품의 경우 시스템 환경변수에 셋팅하는 경우가 가장 많고

인터맥스는 w3wp 프로세스에만 셋팅을 하게 됨

상위인 시스템환경변수 값을 가지고 가며 인터맥스 값은 무시 \.

대응방법은 Uninstall 또는 해당 솔루션이 지정한 cor\_profiler 삭제

![](img%5CDotnet_60.png)

__8\. __  __트러블 슈팅 __

__5\) __  __설치 제거 방법 __  __\( Uninstall __  __과 __  __profile\_for\_service\_stop\.bat\)__

__Uninstall\.bat __  __실행시__  __ __

__profile\_for\_service\_stop\.bat__

![](img%5CDotnet_61.png)

![](img%5CDotnet_62.png)

Regstry 에서 Cor\_profiler만 삭제

성능 또는 이슈로 인해

일시적으로 모니터링을 잠시 빼는 경우 사용

Assembly \, dll \, Resgtry 에서 인터맥스 삭제

__9\. __  __기타 __

Profile\.advice

__\[option\]\[assembly\]:\[class\]:\[method\]:\[callback id\]__

\#    option: '\!'\,'^'\,'~' 에서 한 개를 지정한다\.

\#             생략 할 경우 profile 대상에 포함된다\.

\#      \!: profile 대상에 강제 포함

\#      ^: profile 대상에서 제외

\#     ~: profile 시 내부 조건\(trace\_code\_depth\)에 의해 대상에서 제외

\#          \(profile\.conf의 \[profile\]trace\_code\_depth 옵션의 값이 0보다 큰 경우 동작\)

예시\)

<span style="color:#ffc000"> __\[option__ </span>  <span style="color:#00b050"> __\]\[assembly\]__ </span>  __:__  <span style="color:#3c81f6"> __\[class\]__ </span>  __:__  <span style="color:#ff470e"> __\[method\]__ </span>  __:__  <span style="color:#7030a0"> __\[callback id\]__ </span>

<span style="color:#ffc000">~</span>  <span style="color:#00b050">ebay\.goods</span>  <span style="color:#00b050">\*</span> : <span style="color:#3c81f6">goodscategory</span>  <span style="color:#3c81f6">\*</span> : <span style="color:#ff470e">buy\*</span> : <span style="color:#7030a0">1000</span>

<span style="color:#ffc000"> __~__ </span>  <span style="color:#00b050"> __NiceTCB__ </span>  <span style="color:#00b050"> __\*__ </span> : <span style="color:#3c81f6"> __\*:__ </span>  <span style="color:#ff470e"> __\*__ </span> : <span style="color:#7030a0"> __1000__ </span>

<span style="color:#ff0000">아래와 같은 모든 </span>  <span style="color:#ff0000">메소드는</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">하지말것</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">\(</span>  <span style="color:#ff0000">장애유발</span>  <span style="color:#ff0000">\) </span>

<span style="color:#ff0000">~\*:\*:\*:1000</span>

assembly = dll 파일명

__9\. __  __기타 __

Assembly 는 IIS 설정의 우측 탐색 메뉴에서 어플리케이션 경로를

찾아가서 dll 파일을 찾고 \,

클래스 메소드는 담당자 또는 개발자 가이드 없이 알 수 없음

![](img%5CDotnet_63.png)

__9\. __  __기타 __

__2\) __  __appcmd__  __ list app  __

intermax\.config\.util\.exe 실행이 불가한 경우가 종종 있음

appcmd\.exe list app /site\.name=“test2” 명령어로 확인

![](img%5CDotnet_64.png)

__9\. __  __기타 __

IIS는 w3wp\.exe 대해 20분 동안 호스팅하고 있는 웹에 요청이 없으면

대기상태로 전환이 되며\(기본 20분\)  재생\( Recycle\) 옵션에 의해 프로세스가 재시작 룰이 있음

대기상태 또는 재생 이후에는 인터맥스 화면에는 Disconnect로 표현이 되고 \,

이후 트랜잭션이 최소 1개의 트랜잭션이 실행 되어야 iis 프로세스가 활성화 됩니다

![](img%5CDotnet_65.png)

![](img%5CDotnet_66.png)

__9\. __  __기타 __

__4\) __  __최신버전 기준 중앙 라이센스 필수 __

5\.3 기준 반드시 중앙라이센스가 필요

따라서 Imxosm 기동 필수

<span style="color:#ff0000">최초 설치 이후 윈도우 서비스의 </span>  <span style="color:#ff0000">imxosm</span>  <span style="color:#ff0000"> </span>  <span style="color:#ff0000">자동 시작 체크를 꼭 확인 필요 </span>

![](img%5CDotnet_67.png)

![](img%5CDotnet_68.png)

__9\. __  __기타 __

net\.wasid 에 wasid를 \, 구분으로 개수 만큼 추가

ex\) default web site/=123\,124\,125\,126

![](img%5CDotnet_69.png)

__9\. JAVA AGENT \(JSPD\)__  __ 와 __  __다른점__  __ __

\(1\) net\.wasid 에 wasid를 일괄로 등록

대상이 엄청 많은 경우에는 담당자와 협의 후 일부만 설치 필요

\(2\) jspd\.prop\.ini 와 같이 개별 옵션 파일이 없음

동일한 호스트 전체에 동시 설정만 가능 \, 화면에서 에이전트 옵션 수정 불가

\(3\) iis 기동 유무와 관계없이 닷넷 어플리케이션\(ex \.aspx\) 호출시 boot

최초에는 w3wp\.exe 프로세스가 올라와도 메모리 사용이 아주 작음

이후 첫번째 호출이 들어오면서 메모리에 인터맥스 라이브러리가 올라가게됨

\(4\) 상위 프로세스의 cor\_profiler 옵션에 해당 프로세스의 값이  무시될 수 있음

\(WAS \, 시스템환경변수 \)

레지스트리에 정확하게 cor\_profiler 옵션이 들어가 있어도 시스템 환경변수에

cor\_profiler 옵션이 있는 경우 개별 프로세스의 레지스트리에 cor\_profiler는 무시됨

이와 같은 경우에는 ProcessExplorer 와 같은 툴을 이용해서 확인 해야 함

__9\. JAVA AGENT \(JSPD\)__  __ 와 __  __다른점__  __ __

\(5\) ext 현재 불가능 \(23\.07\.04\)

옵션으로 아래 두가지 정도 가능하고 \, 그 외 요청시에는 연구소로 문의 필요

메소드 파라미터 값 추출 하여 트랜잭션 명으로 표현

메소드 파라미터 값 추출 하여 콜트리에 매개변수 컬럼에 표현

\(6\) 소스 디컴파일 불가 \( Jennifer 도 동일 \)

콜트리 추가 설정시 doPeek 등 프로그램 사용하여 디컴파일 가능하긴함\.

닷넷 설치시 패키지 제품이 아닌 경우에는 개발자가 상주하고 있음\.

개발자에게 문의 또는 ~Assembly:\*:\*:1000

__9\. JAVA AGENT \(JSPD\)__  __ 와 __  __다른점__  __ __

\(7\) IIS 재생\(Recycle\) 정책에 따라 메모리 사용량 또는 시간에 의해 디스커넥트 되는 경우가 있음

호출이 들어오면 다시 연결됨\. 인터맥스 버그로 오해할 가능성이 있음

이러한 동작방식은 IIS의 특징으로 지원하는 엔지니어가 이해하고 고객에게 설명할 수 있어야함\.

\(8\) \.NET 설치 이슈 발생의 경우

JAVA 설치시 일부 데이터가 안보이는 정도가 아니라

실제 IIS 서비스가 불가한 현상이 발생됨

<span style="color:#ff0000">반드시 설치 후 </span>  <span style="color:#ff0000">재기동</span>  <span style="color:#ff0000"> 후 서비스 정상 확인이 필요함 </span>

감사합니다

