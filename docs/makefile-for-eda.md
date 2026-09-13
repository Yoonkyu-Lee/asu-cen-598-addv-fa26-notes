# EDA 흐름에서 Makefile 읽는 법

Lab 0 이 "**각 Makefile 의 타겟을 살펴보라**"고 한 데는 이유가 있다.
이 판에서 Makefile 은 빌드 도구라기보다 **명령 모음집**이다.
타겟을 읽으면 그 도구를 어떤 옵션으로 부르는지가 그대로 드러난다.

소프트웨어 쪽 `make` 를 알더라도 EDA 쪽 관용이 달라서 한 번 정리해둔다.

## 1. 구조: 타겟, 의존성, 레시피

```make
타겟: 의존성
	레시피
```

```make
compile:
	vcs -full64 -sverilog design.v tb.v -debug_access+all |& tee compile.log
```

- **타겟(target)** `compile`. `make compile` 로 부르는 이름이다
- **의존성(prerequisite)** `:` 뒤. 이 타겟 전에 먼저 만들어야 하는 것
- **레시피(recipe)** 아래 줄. **반드시 탭으로 들여쓴다.** 스페이스면 에러가 난다

`make` 를 인자 없이 부르면 **파일에서 첫 번째 타겟**이 돈다. 보통 `all` 을 맨 위에 둔다.

```make
all: sim clean
```

`all` 은 자기 레시피가 없고 의존성만 있다. `make` 라고만 치면 `sim` 을 돌리고 `clean` 을 돌린다는 뜻이다.

## 2. EDA Makefile 이 소프트웨어 Makefile 과 다른 점

소프트웨어 `make` 는 **파일 타임스탬프를 비교해서 바뀐 것만 다시 빌드**하는 게 핵심이다.
EDA Makefile 은 대개 그 기능을 안 쓴다. 타겟 이름이 **파일 이름이 아니라 동작 이름**이다.

```make
sim:
	./simv
```

`sim` 이라는 파일을 만드는 게 아니라 시뮬레이터를 실행할 뿐이다.
그래서 EDA Makefile 은 사실상 **이름 붙인 스크립트 묶음**에 가깝다.

> 엄밀히는 이런 타겟에 `.PHONY: sim` 을 선언해야 `sim` 이라는 파일이 생겼을 때
> 안 도는 사고를 막는다. 강의에서 주는 Makefile 에는 없는 경우가 많다.
> `clean` 이 갑자기 "nothing to be done" 이라고 하면 이걸 의심한다.

## 3. 타겟만 빠르게 뽑아보기

파일이 길면 타겟 목록부터 본다. 줄 맨 앞에서 시작해 `:` 로 끝나는 게 타겟이다.

```bash
grep -nE "^[a-zA-Z_][a-zA-Z0-9_]*:" Makefile
```

레시피는 탭으로 들여써 있어서 `^` 앵커에 안 걸린다. 그래서 타겟만 깔끔하게 나온다.

## 4. 자주 만나는 관용구

### `|& tee` : 화면에도 뿌리고 파일로도 남긴다

```make
	vcs ... |& tee compile.log
```

`tee` 는 입력을 화면과 파일로 동시에 보낸다.
`|&` 는 **stdout 과 stderr 를 함께** 파이프로 넘긴다는 뜻이다 (`2>&1 |` 와 같다).
도구 에러는 stderr 로 나오는 경우가 많아서, 그냥 `| tee` 로 하면
**정작 중요한 에러가 로그에 안 남는다.**

### 변수 확장: `${VCS_HOME}` 과 `$(VERDI_HOME)`

```make
	${VCS_HOME}/bin/vcs ...
	$(VERDI_HOME)/bin/verdi ...
```

`${}` 와 `$()` 는 make 에서 같다. 섞여 있어도 같은 뜻이다.
이 변수들은 **환경 설정 스크립트를 source 해야 잡힌다.** 안 잡히면 경로가 빈 문자열이 되어
`/bin/vcs: No such file` 같은 엉뚱한 에러가 난다.

### `clean` : 산출물을 지운다

```make
clean:
	\rm -rf csrc simv simv.daidir *.log ...
```

`rm` 앞의 백슬래시는 **alias 를 무시하고 원래 명령을 쓰겠다**는 뜻이다.
`rm` 이 `rm -i` 로 alias 되어 있으면 지울 때마다 확인을 묻는데, 그걸 피한다.

`clean` 은 **무엇이 산출물인지 알려주는 목록**이기도 하다.
`clean` 에 적힌 이름들이 곧 그 흐름이 만들어내는 것들이다. 리포트에 "생성된 파일" 을 적어야 할 때
여기부터 보면 빠르다.

## 5. 환경이 먼저다

EDA Makefile 은 거의 다 **환경 변수에 의존한다.** 실행 전에 설정 스크립트를 source 해야 한다.

**이 과목에서 주는 `env.cshrc` 는 tcsh 전용이다.** bash 에서 source 하면 이렇게 된다.

```
bash: setenv: command not found
bash: setenv: command not found
...
```

`setenv` 는 tcsh 문법이라 bash 가 모른다. 문제는 **여기서 멈추지 않는다**는 것이다.
에러만 뿌리고 프롬프트로 돌아오니 성공한 줄 알고 `make` 를 돌리게 된다.

```bash
tcsh                  # 먼저 tcsh 로 들어간다
source env.cshrc      # 그 다음 source
```

터미널을 새로 열면 다시 해야 한다. 환경은 셸마다 따로다.

**tcsh 에서는 리다이렉션 문법도 다르다.** `2>&1` 을 쓰면 `Ambiguous output redirect.` 가 난다.
tcsh 에서는 `>&` 를 쓴다.

| 하려는 것 | bash | tcsh |
|---|---|---|
| stdout + stderr 를 파일로 | `cmd > f 2>&1` | `cmd >& f` |
| 변수 설정 | `export X=1` | `setenv X 1` |

## 6. 이 과목에서 만나는 타겟들

Lab 0 의 `sim/Makefile` 과 `synth/Makefile` 을 읽으면 이런 갈래가 보인다.

| 갈래 | 하는 일 | 읽을 때 볼 것 |
|---|---|---|
| 컴파일 계열 | 설계와 testbench 를 VCS 로 컴파일 | **옵션 차이**. 디버그용과 일반용이 갈린다 |
| 실행 계열 | 만들어진 시뮬레이터 실행파일을 돌린다 | plusarg 로 테스트를 고르는지 |
| 디버거 계열 | Verdi 를 띄운다 | 설계 DB 와 파형 DB 를 각각 어떻게 넘기는지 |
| 합성 계열 | Design Compiler 에 스크립트를 먹인다 | 어떤 `.tcl` 을 넘기는지 |
| 청소 계열 | 산출물 삭제 | 무엇이 산출물인지의 목록 |

**같은 도구를 부르는데 타겟이 여러 개면 옵션이 다르다는 뜻이다.** 거기가 핵심이다.
예를 들어 Verdi 로 디버그하려면 컴파일 때 knowledge database 를 만들어야 하는데,
그 스위치가 붙은 타겟은 따로 있다. 일반 컴파일 결과로는 Verdi 가 설계를 못 읽는다.
Lab 0 안내도 `make compile_verdi` 를 예로 든다.

## 7. 읽는 순서

1. **타겟 목록**을 뽑는다 (`grep`)
2. `all` 이 무엇에 의존하는지 본다. 기본 동작이 드러난다
3. **같은 도구를 부르는 타겟들을 나란히 놓고 옵션을 비교한다.** 차이가 곧 그 타겟의 목적이다
4. `clean` 을 읽는다. 산출물 목록이 공짜로 나온다
5. 변수(`${...}`)가 어디서 오는지 확인한다. 환경 설정 스크립트를 찾아 먼저 source 한다

## 더 보기

- GNU Make 매뉴얼: https://www.gnu.org/software/make/manual/
- `.PHONY` 설명: https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
