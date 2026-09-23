# -*- coding: utf-8 -*-
"""Lab 1 코드 뷰어 · Part 1 빌드와 수정 커밋, Part 2 전부, 커밋 히스토리."""
from codeview_build import C, F, N, T

P1 = 'lab1/part1/'
P2 = 'lab1/part2/'
TB1 = P1 + 'tb_async_fifo.sv'
TBE = P2 + 'tb/tb_even_odd.sv'
TBF = P2 + 'tb/tb_fifo_q.sv'

# ════════════════════════════════════════════════════════════════ p1fix
# 07 절. Test 2 를 고친 두 커밋.

P1FIX = [
    C('755a20f',
      note=T('Test 2 가 <strong>플래그가 언젠가 서기만 하면</strong> 통과하던 것을, 문턱 양쪽을 재도록 바꿨다. 이 커밋 전에 설계의 문턱을 <code>DEPTH / 2</code> 로 일부러 틀려봤고, 옛 Test 2 는 그래도 통과했다.',
             'Test 2 used to pass <strong>as long as the flag ever rose</strong>; now it checks both sides of each threshold. Before this commit the design\'s threshold was deliberately broken to <code>DEPTH / 2</code>, and the old Test 2 still passed.'),
      notes={TB1: [
          ('localparam int AF_LEVEL', '문턱을 설계와 같은 식으로 뽑았다. 숫자 12 와 8 이 사라진다.', 'The thresholds are pulled out, written like the design writes them. The literal 12 and 8 disappear.'),
          ('-for (i = 0; i < 12; i = i + 1)', '옛 판은 <strong>12 개를 한꺼번에</strong> 넣었다. 12 는 문턱 그 자체라서 11 에서 내려가 있었는지는 볼 기회가 없다.', 'The old version wrote <strong>all 12 at once.</strong> 12 is the threshold itself, so there was never a moment to see whether the flag was still low at 11.'),
          ('for (i = 0; i < AF_LEVEL - 1; i = i + 1)', '새 판은 <strong>하나 모자라게</strong> 11 개만 넣는다.', 'The new version writes <strong>one short</strong>: 11.'),
          ('-wait (almost_full);', '<strong>이 줄이 문제였다.</strong> <code>wait</code> 는 언젠가 참이 되기만 하면 지나간다. 8 에서 서든 12 에서 서든 똑같이 통과한다.', '<strong>This was the line at fault.</strong> <code>wait</code> passes the moment the condition is ever true. Rising at 8 or at 12 passes just the same.'),
          ('-$display("almost_full asserted at 3/4 full.");', '<strong>상수 문자열.</strong> 무슨 일이 일어났든 "3/4" 라고 찍는다.', '<strong>A constant string.</strong> Whatever happened, it said "3/4".'),
          ('@(posedge wclk);', '11 개 뒤 한 엣지. 등록된 플래그가 반영될 시간이다. 여기서 서 있으면 <strong>일찍 선 것</strong>이다.', 'One edge after 11, time for the registered flag to catch up. High here means it <strong>rose early.</strong>'),
          ('write_word(8\'h20 + AF_LEVEL - 1);', '12 번째. 이 뒤에는 <strong>서 있어야</strong> 한다.', 'The 12th; after this it <strong>must</strong> be high.'),
          ('$display("almost_full correct:', '성공 문구를 새로 썼다. 그런데 <strong>조건 없이</strong> 찍힌다. 다음 커밋이 이걸 고친다.', 'A new success message, but printed <strong>unconditionally.</strong> The next commit fixes that.'),
          ('for (i = 0; i < AF_LEVEL - AE_LEVEL - 1; i = i + 1)', '12 개 든 상태에서 7 개를 꺼내면 5 개가 남는다. 문턱 4 보다 하나 많다. 옛 판의 8 개는 4 를 남겨 문턱에 바로 떨어졌다.', 'With 12 inside, taking 7 leaves 5: one above the threshold of 4. The old version took 8 and landed right on 4.'),
          ('@(posedge rclk);', '읽기 쪽 플래그라 <code>rclk</code> 으로 기다린다.', 'A read-side flag, so wait on <code>rclk</code>.'),
      ]}),
    C('ec8e782',
      note=T('고친 판이 자기가 비판한 실수를 반복했다. 검사가 실패해도 바로 밑에 "correct" 가 찍혔다. 에러 수를 적어두고 안 늘었을 때만 찍게 했다.',
             'The fix had repeated the flaw it criticised: "correct" printed right under a failed check. Now the error count is noted and the message prints only if it has not grown.'),
      notes={TB1: [
          ('integer err_mark;', '표시해 둘 변수 하나.', 'One variable to hold the mark.'),
          ('err_mark = errors;', 'almost_full 검사를 시작하기 전의 에러 수.', 'The error count before the almost_full checks start.'),
          ('if (errors == err_mark)', '그 사이에 에러가 하나도 안 났을 때만 "correct" 를 찍는다.', '"correct" prints only if no error occurred in between.'),
      ]}),
]

# ════════════════════════════════════════════════════════════════ p1build
# 06 절. Makefile 과 환경 파일.

P1BUILD_FILES = [
    F(P1 + 'Makefile', role='t', key='mk1', label='part1/Makefile',
      sum=T('한 번 컴파일하고 테스트는 plusarg 로 바꿔 돌린다. target 은 <code>compile</code>, <code>test1..3</code>, <code>verdi</code>, <code>trace</code>, <code>clean</code>.',
            'Compile once, switch tests by plusarg. Targets: <code>compile</code>, <code>test1..3</code>, <code>verdi</code>, <code>trace</code>, <code>clean</code>.'),
      notes=[
        ('SOURCES = fifo_if.sv', '<strong>순서가 의미 있다.</strong> interface 가 먼저 와야 그걸 쓰는 <code>fifo_mem</code> 이 컴파일될 때 이미 알려져 있다. 맨 끝이 testbench 다.', '<strong>The order matters.</strong> The interface comes first so it is already known when <code>fifo_mem</code>, which uses it, compiles. The testbench goes last.'),
        ('VCS = $(VCS_HOME)/bin/vcs', '도구를 <code>VCS_HOME</code> 에서 찾는다. 환경 파일을 안 읽었으면 여기가 <code>/bin/vcs</code> 가 되어 "command not found" 가 난다.', 'The tool is found under <code>VCS_HOME</code>. Skip the environment file and this becomes <code>/bin/vcs</code>, hence "command not found".'),
        ('$(VCS) -full64 -sverilog -timescale=1ns/1ps', '<code>-sverilog</code> 가 SystemVerilog 를 켠다. <code>-timescale=1ns/1ps</code> 는 <code>#5</code> 같은 지연의 단위를 정한다. 파일마다 <code>`timescale</code> 을 안 적었으므로 여기서 준다.', '<code>-sverilog</code> turns on SystemVerilog. <code>-timescale=1ns/1ps</code> sets the unit of delays like <code>#5</code>; no file has its own <code>`timescale</code>, so it comes from here.'),
        ('tb_async_fifo -debug_access+all -kdb -lca', '<code>-top</code> 이 최상위를 지정한다. <code>-debug_access+all</code> 은 모든 신호를 볼 수 있게 하고, <code>-kdb</code> 는 Verdi 가 설계 구조를 읽을 데이터베이스를 만든다. <code>-lca</code> 는 Synopsys 가 LCA (Limited Customer Availability) 로 분류한 기능을 켠다.', '<code>-top</code> names the top level. <code>-debug_access+all</code> makes every signal visible, <code>-kdb</code> writes the database Verdi reads the design structure from, and <code>-lca</code> enables features Synopsys classes as LCA (Limited Customer Availability).'),
        ('./simv +TEST_FILL_EMPTY', '실행 파일은 하나다. plusarg 만 바꾼다.', 'One executable; only the plusarg changes.'),
        ('$(VERDI) -dbdir ./simv.daidir -ssf novas.fsdb', '설계 데이터베이스와 파형 파일을 함께 넘겨서 연다.', 'Opens with both the design database and the waveform file.'),
        ('trace: compile', '셋을 차례로 돌리며 각각 CSV 를 남긴다. 이 페이지 파형의 출처다.', 'Runs all three in turn, leaving one CSV each. The source of this page\'s waveforms.'),
      ]),
    F(P1 + 'env.sh', role='t', key='envsh', label='part1/env.sh',
      sum=T('bash 용. Apporto 터미널의 기본 셸이 bash 다.', 'For bash, the default shell in an Apporto terminal.'),
      notes=[
        ('export PATH=/usr/local2/synopsys/verdi', '도구 셋의 경로. Verdi, VCS, 그리고 Design Compiler (<code>syn</code>). Lab 1 에서 DC 는 안 쓴다. 들어 있어도 해는 없다.', 'Paths for three tools: Verdi, VCS and Design Compiler (<code>syn</code>). Lab 1 never runs DC; having it there does no harm.'),
        ('export VCS_HOME=', 'Makefile 이 이 두 변수로 도구를 찾는다.', 'The Makefile finds the tools through these two.'),
        ('export LM_LICENSE_FILE=', '<strong>라이선스 서버.</strong> VCS 와 Verdi 가 여기서 라이선스를 받는다. 두 변수가 같은 서버를 가리킨다.', '<strong>The licence server.</strong> VCS and Verdi check out their licences here; both variables point at the same server.'),
        ('export LD_LIBRARY_PATH=/usr/local2/synopsys/verdi_2024.09/verdi_2024/share/PLI', 'testbench 의 <code>$fsdbDumpfile</code> 이 쓰는 Verdi 라이브러리 경로. 둘째 줄은 Verdi 화면이 쓰는 Qt 라이브러리다.', 'Where the Verdi library behind the testbench\'s <code>$fsdbDumpfile</code> lives. The second line is the Qt library the Verdi GUI uses.'),
        ('export PDK_DIR=', 'FreePDK45 경로. Lab 1 은 안 쓴다.', 'The FreePDK45 path, unused in Lab 1.'),
      ]),
    F(P1 + 'env.cshrc', role='t', key='envcsh', label='part1/env.cshrc',
      sum=T('csh 용. 내용은 <code>env.sh</code> 와 같고 <code>export A=B</code> 가 <code>setenv A B</code> 로 바뀌었을 뿐이다. 먼저 생긴 쪽은 이것이다.', 'For csh. Same content as <code>env.sh</code>, with <code>export A=B</code> written <code>setenv A B</code>. This one came first.')),
]

P1BUILD_TREES = [
    (T('파일', 'files'), [
        N('part1', kids=[N('Makefile', file='mk1'), N('env.sh', file='envsh', badge='bash'), N('env.cshrc', file='envcsh', badge='csh')])]),
]

# ════════════════════════════════════════════════════════════════ p2
# 11 절. Part 2 RTL 전문. 전부 새로 쓴 파일이라 diff 가 아니라 원문이다.

P2_FILES = [
    F(P2 + 'rtl/even_odd_top.sv', key='top', label='rtl/even_odd_top.sv',
      sum=T('회로 전체. 쓰기 쪽 분배, FIFO 둘, 읽기 쪽 교대 선택, 출력 레지스터. 위에서 아래로 데이터가 흐르는 순서대로 적혀 있다.',
            'The whole circuit: write-side routing, two FIFOs, read-side alternation, output register. It reads top to bottom in the order data flows.'),
      notes=[
        ('parameter int FIFO_DEPTH = 64', '기본값 64 는 비동기 판에 맞춘 값이다. 실제 깊이는 Makefile 이 넘긴다. 동기 40, 비동기 64.', 'The default of 64 suits the async variant. The real depth comes from the Makefile: 40 sync, 64 async.'),
        ('input  logic                  Clock,', '포트 이름은 Lab 이 준 그대로다. <code>Clock</code>, <code>Reset</code>, <code>Data_in</code>, <code>Write_en</code>, <code>Data_out</code>, <code>Read_en</code>. 대문자로 시작하는 것도 그대로 뒀다.', 'Port names exactly as the lab gives them, capitals included: <code>Clock</code>, <code>Reset</code>, <code>Data_in</code>, <code>Write_en</code>, <code>Data_out</code>, <code>Read_en</code>.'),
        ('assign rst_n = ~Reset;', 'Lab 의 <code>Reset</code> 은 1 일 때 reset 이다. FIFO 들은 0 일 때 reset 이다 (<code>rst_n</code>). 뒤집어서 넘긴다.', 'The lab\'s <code>Reset</code> is active high; the FIFOs take active-low <code>rst_n</code>. It is inverted on the way.'),
        ('even_wr_en = Write_en && (Data_in[0] == 1\'b0);', '<strong>짝홀은 맨 아래 비트 하나로 갈린다.</strong> 0 이면 짝수 FIFO 로, 1 이면 홀수 FIFO 로. 한 사이클에 둘 중 정확히 하나만 켜진다.', '<strong>Parity is the bottom bit alone.</strong> 0 goes to the even FIFO, 1 to the odd. Exactly one of the two is on in any cycle.'),
        ('fifo_q #(', '<strong>여기서 <code>fifo_q</code> 가 어느 쪽인지 이 파일은 모른다.</strong> 같은 이름의 모듈이 <code>rtl/sync/</code> 와 <code>rtl/async/</code> 에 하나씩 있고, Makefile 이 둘 중 하나만 컴파일에 넣는다. 이 파일은 한 글자도 안 바뀐다.', '<strong>This file does not know which <code>fifo_q</code> it gets.</strong> A module of that name exists in both <code>rtl/sync/</code> and <code>rtl/async/</code>, and the Makefile compiles only one. Not a character here changes.'),
        ('.wr_data (Data_in),', '데이터는 두 FIFO 에 <strong>똑같이</strong> 물린다. 누가 받을지는 <code>wr_en</code> 이 정한다.', 'Data goes to <strong>both</strong> FIFOs; <code>wr_en</code> decides which one takes it.'),
        ('typedef enum logic {', '<strong>상태가 둘뿐인 FSM.</strong> 다음에 짝수를 낼 차례인가, 홀수를 낼 차례인가. 1 비트 enum 이라 파형에서도 이름으로 보인다.', '<strong>An FSM with two states:</strong> is it even\'s turn or odd\'s. A one-bit enum, so the waveform shows the names.'),
        ('logic started;', '<strong>첫 출력의 짝홀을 정하는 깃발.</strong> Lab 은 첫 출력이 짝수여야 한다고 정하지 않았다. 그래서 <strong>처음 들어온 값의 짝홀</strong>로 시작한다. 그러지 않고 짝수로 못박으면, 홀수가 먼저 들어왔을 때 짝수가 올 때까지 출력이 멈춘다.', '<strong>The flag that fixes the first output\'s parity.</strong> The lab does not say the first output must be even, so it starts with <strong>the parity of the first value in.</strong> Pinning it to even would stall output whenever an odd number arrived first.'),
        ('sel_empty = (sel == SEL_EVEN) ? even_empty   : odd_empty;', '지금 차례인 FIFO 의 empty 와 머리 값을 고른다. 2:1 mux 둘이다.', 'Pick the empty flag and head value of whichever FIFO\'s turn it is: two 2:1 muxes.'),
        ('assign do_pop = Read_en && !sel_empty;', '<strong>이 회로의 핵심 한 줄.</strong> 읽으라고 했고 차례인 FIFO 에 뭔가 있을 때만 꺼낸다. <strong>차례인 쪽이 비었으면 다른 쪽에 값이 있어도 안 꺼낸다.</strong> 그래야 같은 짝홀이 두 번 연속 안 나온다. 이게 Lab 이 말한 "pause" 다.', '<strong>The key line.</strong> Pop only when asked to and the FIFO whose turn it is has something. <strong>If that FIFO is empty, nothing pops even if the other one has data.</strong> That is how two of the same parity never come out in a row, and it is the "pause" the lab describes.'),
        ('even_rd_en = do_pop && (sel == SEL_EVEN);', '꺼내기를 차례인 FIFO 에만 보낸다.', 'The pop goes to the FIFO whose turn it is, and only that one.'),
        ('logic out_valid;', '<strong>포트가 아닌 내부 신호다.</strong> "이번 엣지에 <code>Data_out</code> 이 새 값을 받았다" 는 뜻이다. Lab 의 포트 목록에 valid 가 없어서 밖으로는 못 낸다. testbench 가 계층 이름 <code>dut.out_valid</code> 로 들여다본다.', '<strong>An internal signal, not a port.</strong> It means "<code>Data_out</code> took a new value on this edge". The lab\'s port list has no valid, so it cannot go outside; the testbench reads it hierarchically as <code>dut.out_valid</code>.'),
        ('always_ff @(posedge Clock) begin', '<strong>여기만 동기 reset 이다.</strong> FIFO 안쪽은 비동기 reset (<code>negedge rst_n</code>) 이지만 이 블록은 <code>Clock</code> 엣지에서만 <code>Reset</code> 을 본다. testbench 가 <code>Reset</code> 을 엣지 여럿에 걸쳐 들고 있으므로 결과는 같다.', '<strong>This block alone resets synchronously.</strong> The FIFOs reset asynchronously (<code>negedge rst_n</code>), but here <code>Reset</code> is seen only on <code>Clock</code> edges. The testbench holds <code>Reset</code> across several edges, so the outcome is the same.'),
        ('Data_out  <= \'0;', 'reset 뒤 <code>Data_out</code> 은 0 이다. Lab 은 <strong>0 을 출력하지 말라</strong>고 했다. 그 뜻은 "멈출 때 0 을 흘리지 말라" 다. 그래서 멈출 때는 <code>Data_out</code> 을 안 바꾸고 옛 값을 붙들어 둔다. reset 직후의 0 은 아직 아무것도 안 낸 상태라 <code>out_valid</code> 가 0 이다.', 'After reset <code>Data_out</code> is 0. The lab says <strong>never output 0</strong>, meaning "do not emit 0 while pausing". So a pause leaves <code>Data_out</code> holding its old value. The 0 right after reset is before anything has been emitted, and <code>out_valid</code> is 0.'),
        ('Data_out <= sel_data;', '<strong>출력이 등록된다.</strong> 머리 값이 다음 엣지에 <code>Data_out</code> 으로 옮겨진다. 출력이 입력을 직접 보지 않으므로 Moore 다 (10 절).', '<strong>The output is registered:</strong> the head value moves into <code>Data_out</code> on the edge. The output never looks straight at an input, so this is Moore (section 10).'),
        ('sel      <= (sel == SEL_EVEN) ? SEL_ODD : SEL_EVEN;', '꺼냈을 때만 차례를 넘긴다. 멈춘 사이클에는 차례가 그대로다.', 'The turn passes only on a pop; in a paused cycle it stays.'),
        ('if (Write_en && !started) begin', '처음 들어온 쓰기에서 딱 한 번. 위의 <code>sel</code> 대입보다 <strong>뒤에 적혀 있어서</strong> 같은 엣지에 둘 다 걸리면 이쪽이 이긴다. 같은 always 블록 안에서 non-blocking 대입이 겹치면 마지막 것이 남는다.', 'Once, on the first write. It is written <strong>after</strong> the <code>sel</code> assignment above, so if both fire on the same edge, this one wins: with overlapping non-blocking assignments in one block, the last one stands.'),
      ]),
    F(P2 + 'rtl/sync/fifo_q.sv', key='syncq', label='rtl/sync/fifo_q.sv',
      sum=T('<strong>동기 FIFO.</strong> clock 하나, 포인터 둘, 그리고 점유량을 직접 세는 카운터 하나. 깊이가 2 의 거듭제곱일 필요가 없다.', '<strong>The synchronous FIFO:</strong> one clock, two pointers, and a counter holding the occupancy directly. The depth need not be a power of two.'),
      notes=[
        ('module fifo_q #(', '<strong>이 포트 목록이 두 구현의 계약이다.</strong> 비동기 판도 글자 하나 다르지 않은 목록을 가진다.', '<strong>This port list is the contract between the two implementations.</strong> The async version has one identical to the letter.'),
        ('output logic [DATA_WIDTH-1:0] rd_data,', '<code>rd_data</code> 는 <strong>지금 머리에 있는 값</strong>이다. <code>rd_en</code> 은 그걸 꺼내는 신호다. Part 1 의 메모리 읽기가 조합이라 비동기 판이 원래 이렇게 동작한다. 동기 판이 거기 맞췄다.', '<code>rd_data</code> is <strong>whatever is at the head right now;</strong> <code>rd_en</code> removes it. Part 1\'s memory reads combinationally, so the async version behaves this way by nature, and the sync version follows it.'),
        ('localparam int PTR_WIDTH = (DEPTH <= 1) ? 1 : $clog2(DEPTH);', '포인터 폭. 깊이 1 이면 <code>$clog2(1) = 0</code> 이라 폭 0 짜리 신호가 된다. 그걸 막는 조건이다.', 'Pointer width. At depth 1, <code>$clog2(1) = 0</code> would give a zero-width signal; the condition prevents it.'),
        ('localparam int CNT_WIDTH = $clog2(DEPTH + 1);', '<strong>카운터는 0 부터 DEPTH 까지</strong> 세야 해서 DEPTH+1 가지 값이 있다. 깊이 64 면 포인터는 6 비트지만 카운터는 7 비트가 필요하다. 깊이 40 이면 둘 다 6 비트다. <code>$clog2(DEPTH)</code> 로 적으면 64 에서만 조용히 틀린다.', '<strong>The counter runs from 0 to DEPTH,</strong> DEPTH+1 values. At depth 64 the pointer is 6 bits but the counter needs 7; at 40 both are 6. Write <code>$clog2(DEPTH)</code> and it breaks silently only at 64.'),
        ('do_wr = wr_en && !full;', '실제로 일어나는 쓰기와 읽기. 가득 찼을 때 쓰기, 비었을 때 읽기는 무시된다.', 'The writes and reads that actually happen; a write when full or a read when empty is ignored.'),
        ('assign full  = (count == CNT_WIDTH\'(DEPTH));', 'full 과 empty 가 카운터에서 <strong>조합으로</strong> 바로 나온다. 쓰고 나서 바로 다음 엣지에 반영된다. 비동기 판과 갈리는 지점이 여기다.', 'full and empty come straight off the counter, <strong>combinationally,</strong> reflecting a write by the very next edge. This is where the two implementations part ways.'),
        ('assign rd_data = mem[rptr];', '읽기는 조합이다. 위의 계약 그대로.', 'A combinational read, as the contract says.'),
        ('wptr      <= (wptr == PTR_WIDTH\'(DEPTH - 1)) ? \'0 : wptr + 1\'b1;', '<strong>끝에서 0 으로 직접 돌린다.</strong> 깊이 40 이면 포인터 6 비트가 63 까지 셀 수 있지만 39 다음에 0 으로 간다. 2 의 거듭제곱이 아니어도 되는 이유가 이 한 줄이다. 비동기 판은 gray code 때문에 이걸 못 한다.', '<strong>Wraps to 0 explicitly at the end.</strong> At depth 40 the 6-bit pointer could count to 63, but after 39 it goes to 0. This one line is why the depth need not be a power of two. The async version cannot do this, because of gray code.'),
        ('unique case ({do_wr, do_rd})', '쓰기만 있으면 +1, 읽기만 있으면 -1, 둘 다 있거나 둘 다 없으면 그대로. <code>unique</code> 는 겹치는 경우가 없다고 도구에 알린다.', 'Write only, +1; read only, -1; both or neither, unchanged. <code>unique</code> tells the tools no two branches overlap.'),
      ]),
    F(P2 + 'rtl/async/fifo_q.sv', key='asyncq', label='rtl/async/fifo_q.sv',
      sum=T('<strong>비동기 판은 Part 1 을 감싼 껍데기다.</strong> 로직은 한 줄도 없다. Part 1 의 파일을 고치지 않고 경로로 가져다 쓴다.', '<strong>The async variant is a shell around Part 1,</strong> with no logic of its own. Part 1\'s files are used by path, untouched.'),
      notes=[
        ('logic almost_full_unused;', 'Part 1 의 3/4 플래그는 여기서 쓸 곳이 없다. 그냥 두면 포트가 비어 경고가 나므로 이름 붙인 선에 받아서 버린다.', 'Part 1\'s 3/4 flags have no use here. Left open they would draw warnings, so they land on named wires and go nowhere.'),
        ('async_fifo #(', '여기서는 <code>.*</code> 를 안 쓴다. 이름이 다르기 때문이다. <code>wr_data</code> 와 <code>wdata</code>, <code>full</code> 과 <code>wfull</code>. 이름으로 하나씩 이어준다.', 'No <code>.*</code> here, because the names differ: <code>wr_data</code> vs <code>wdata</code>, <code>full</code> vs <code>wfull</code>. Each is connected by name.'),
        ('.wclk   (clk),', '<strong>두 clock 에 같은 <code>clk</code> 을 물린다.</strong> 그래도 안쪽 동기화기 두 단은 그대로 남는다. 회로는 clock 이 같은 줄 모른다. 그래서 empty 가 3 엣지 늦게 풀린다.', '<strong>The same <code>clk</code> drives both clocks.</strong> The two synchroniser stages inside remain all the same: the circuit has no idea the clocks match. That is why empty clears three edges late.'),
        ('.wrst_n (rst_n),', 'reset 도 하나를 양쪽에.', 'One reset to both sides, likewise.'),
      ]),
]

P2_TREES = [
    (T('모듈 계층', 'module hierarchy'), [
        N('even_odd_top', file='top', kids=[
            N(T('쓰기 분배 (Data_in[0])', 'write routing (Data_in[0])'), file='top', at='even_wr_en = Write_en'),
            N('u_fifo_even : fifo_q', file='syncq', badge='VARIANT', kids=[
                N(T('sync: rtl/sync/fifo_q.sv', 'sync: rtl/sync/fifo_q.sv'), file='syncq'),
                N(T('async: rtl/async/fifo_q.sv', 'async: rtl/async/fifo_q.sv'), file='asyncq', kids=[
                    N(T('u_async_fifo : async_fifo  (Part 1)', 'u_async_fifo : async_fifo  (Part 1)'), file='asyncq', at='async_fifo #(')])]),
            N('u_fifo_odd : fifo_q', file='top', at='u_fifo_odd'),
            N(T('교대 FSM (sel · started)', 'alternation FSM (sel · started)'), file='top', at='typedef enum logic {'),
            N('do_pop', file='top', at='assign do_pop'),
            N(T('출력 레지스터', 'output register'), file='top', at='always_ff @(posedge Clock)')])]),
    (T('파일', 'files'), [
        N('part2/rtl', kids=[
            N('even_odd_top.sv', file='top'),
            N('sync/fifo_q.sv', file='syncq'),
            N('async/fifo_q.sv', file='asyncq', badge='→ ../part1')])]),
]

# ════════════════════════════════════════════════════════════════ p2tb
# 12 절. testbench 둘.

P2TB_FILES = [
    F(TBF, role='v', key='tbf', label='tb/tb_fifo_q.sv',
      sum=T('<strong>층 1.</strong> 두 FIFO 구현이 같은 계약을 지키는지 본다. 그리고 empty 가 몇 엣지 늦게 풀리는지를 잰다.', '<strong>Layer 1.</strong> Do both FIFO implementations keep the same contract, and how many edges late does empty clear.'),
      notes=[
        ('`ifndef FIFO_DEPTH', '깊이는 컴파일할 때 <code>+define+FIFO_DEPTH=</code> 로 들어온다. 안 들어오면 64.', 'The depth arrives at compile time via <code>+define+FIFO_DEPTH=</code>; 64 if it does not.'),
        ('fifo_q #(', '<code>.*</code> 로 붙는다. 선언한 신호 이름이 계약의 포트 이름과 같기 때문이다. 이 testbench 는 어느 <code>fifo_q</code> 가 붙었는지 모른다.', 'Connected with <code>.*</code>, because the signal names match the contract\'s ports. The testbench has no idea which <code>fifo_q</code> it got.'),
        ('task automatic push(', '쓰기 한 번. negedge 에 올리고 다음 negedge 에 내린다. 그 사이의 posedge 에서 FIFO 가 받는다.', 'One write: raise on a negedge, drop on the next. The FIFO takes it on the posedge between.'),
        ('d     = rd_data;', '머리 값을 먼저 읽고 <code>rd_en</code> 을 올린다. 계약이 그렇게 생겼다.', 'Read the head, then raise <code>rd_en</code>, as the contract says.'),
        ('task automatic measure_empty_latency;', '<strong>empty 지연 재기.</strong> 비어 있는 FIFO 에 하나를 넣고, 그 뒤 엣지마다 empty 를 본다. 몇 번째 엣지에서 풀리는지가 답이다. 동기 0, 비동기 3.', '<strong>Measuring the empty latency.</strong> Put one item into an empty FIFO and look at empty after every edge. The edge on which it clears is the answer: 0 sync, 3 async.'),
        ('#1;', '<strong>엣지 1 ns 뒤에 읽는다.</strong> 엣지 순간에 읽으면 설계가 아직 그 엣지의 결과를 안 냈다. 한 번 더 세게 되어 4 가 나왔다. 14 절에 있는 버그이고 아래 커밋 뷰어에 고친 커밋이 있다.', '<strong>Read 1 ns after the edge.</strong> Read at the edge itself and the design has not yet produced that edge\'s result, so one extra edge gets counted and you get 4. It is the bug in section 14; the commit viewer below has the fix.'),
        ('task automatic fill_and_drain;', '끝까지 채워 full 이 서는지, 다 빼서 순서가 맞고 empty 가 서는지. 비동기 판은 플래그가 늦으므로 판정 전에 4 엣지 기다린다.', 'Fill to full and check full; drain and check the order and empty. The async flags lag, so each check waits 4 edges first.'),
        ('task automatic stream;', '8 개를 먼저 넣고, 24 번을 <strong>한 사이클에 읽기와 쓰기를 같이</strong> 한다. 동기 판의 카운터가 둘 다 있을 때 그대로인지 여기서 걸린다.', 'Preload 8, then 24 cycles of <strong>reading and writing in the same cycle.</strong> This is where the sync counter\'s both-at-once case gets exercised.'),
      ]),
    F(TBE, role='v', key='tbe', label='tb/tb_even_odd.sv',
      sum=T('<strong>층 2.</strong> 회로 전체를 문서의 case 넷으로 돌린다. producer, consumer, monitor 셋이 동시에 돈다.', '<strong>Layer 2.</strong> The whole circuit through four cases from the document, with a producer, a consumer and a monitor running concurrently.'),
      notes=[
        ('localparam int N_ITEMS = 80;', 'case 하나에 80 개. 짝수 40, 홀수 40 이다.', '80 items per case: 40 even, 40 odd.'),
        ('logic [DATA_WIDTH-1:0] exp_even [$];', '<strong>예상값 queue 둘.</strong> 쓸 때 짝홀에 맞춰 넣고, 나올 때 앞에서 꺼내 비교한다. 짝수끼리, 홀수끼리의 순서를 따로 본다.', '<strong>Two expected-value queues.</strong> Pushed by parity when written, popped from the front when output. Order is checked within evens and within odds separately.'),
        ('int occ_even, occ_odd;', '점유량을 <strong>FIFO 밖에서</strong> 센다. 두 구현이 안에 들고 있는 신호가 다르므로 (카운터 대 gray 포인터) 밖의 <code>wr_en</code>·<code>rd_en</code> 으로 세야 같은 잣대가 된다.', 'Occupancy is counted <strong>outside the FIFOs.</strong> The two implementations hold different internal signals (a counter vs gray pointers), so counting the outer <code>wr_en</code>/<code>rd_en</code> is the only common yardstick.'),
        ('time start_time;', 'case 가 걸린 시간. 첫 쓰기부터 마지막 출력까지.', 'How long a case takes, first write to last output.'),
        ('always @(posedge Clock) begin', '<strong>점유량 추적기. 엣지 그 순간에 읽는다.</strong> 이 엣지가 실제로 쓰고 꺼내는 값을 보려면 설계가 바뀌기 전에 봐야 한다. 처음 판은 여기 <code>#1</code> 이 있었고 다음 엣지의 꺼내기를 미리 셌다 (14 절).', '<strong>The occupancy tracker, reading at the edge itself.</strong> To see what this edge actually writes and pops, look before the design changes. The first version had a <code>#1</code> here and counted the next edge\'s pop early (section 14).'),
        ('if (dut.even_rd_en)', '<code>even_rd_en</code> 은 이미 <code>do_pop</code> 을 품고 있어서 비었을 때는 안 켜진다. 그래서 따로 empty 를 안 본다.', '<code>even_rd_en</code> already contains <code>do_pop</code> and never fires when empty, so empty needs no separate check.'),
        ('if (dut.even_full || dut.odd_full) full_seen = full_seen + 1;', '<strong>한 번이라도 가득 차면 실패.</strong> 가득 차면 쓰기가 버려지므로 데이터를 잃는다. 깊이가 모자라다는 뜻이다.', '<strong>Going full even once is a failure:</strong> a write while full is dropped, so data is lost. It means the depth is too small.'),
        ('#2;', '추적 파일은 엣지 2 ns 뒤에 찍는다. 이번엔 엣지의 <strong>결과</strong>를 남기고 싶어서다. 추적기와 반대 시점이다.', 'The trace file is written 2 ns after the edge, because here we want the edge\'s <strong>result.</strong> The opposite timing from the tracker.'),
        ('task automatic build_stim(', '자극 80 개. 짝수 2..80 과 홀수 1..79.', 'The 80 stimuli: evens 2..80 and odds 1..79.'),
        ('if (!skew) begin', '<code>skew</code> 가 아니면 섞는다 (Fisher-Yates). skew 면 <strong>짝수 40 개가 먼저 다 들어오고 홀수가 뒤에</strong> 온다. 한쪽 FIFO 에 몰리는 최악이다.', 'Without <code>skew</code>, shuffle (Fisher-Yates). With it, <strong>all 40 evens arrive first and the odds after:</strong> the worst case, everything piling into one FIFO.'),
        ('task automatic producer(', '<code>wr_period</code> 사이클마다 앞의 <code>wr_on</code> 사이클 동안 쓴다. 문서의 "100 사이클에 80 번 쓰기" 가 <code>(80, 100)</code> 이다.', 'Writes during the first <code>wr_on</code> cycles of every <code>wr_period</code>. The document\'s "80 writes per 100 cycles" is <code>(80, 100)</code>.'),
        ('task automatic consumer(', '같은 방식으로 <code>Read_en</code> 을 켠다. 켜도 차례인 FIFO 가 비었으면 회로가 안 꺼낸다. 그 판단은 회로 몫이다.', '<code>Read_en</code> the same way. Even when it is on, the circuit will not pop if the FIFO whose turn it is is empty; that call is the circuit\'s.'),
        ('if (dut.out_valid) begin', '회로가 새 값을 낸 사이클만 본다. 내부 신호를 계층 이름으로 들여다본다.', 'Only cycles where the circuit emitted a new value, read through the internal signal by hierarchical name.'),
        ('if (d === \'0) begin', '규칙 1. <strong>0 을 내지 않는다.</strong>', 'Rule 1: <strong>never output 0.</strong>'),
        ('if (prev_parity >= 0 && int\'(d[0]) == prev_parity) begin', '규칙 2. <strong>같은 짝홀이 두 번 연속 안 나온다.</strong> 첫 출력은 비교할 것이 없어서 -1 로 시작한다.', 'Rule 2: <strong>never the same parity twice in a row.</strong> The first output has nothing to compare with, so this starts at -1.'),
        ('want = exp_odd.pop_front();', '규칙 3. <strong>홀수끼리 들어간 순서대로 나온다.</strong> 짝수도 아래에서 같이.', 'Rule 3: <strong>odds come out in the order they went in;</strong> evens likewise below.'),
        ('task automatic run_case(', 'case 하나를 돌린다. 상태를 비우고, reset 하고, 자극을 만들고, 셋을 동시에 띄운다.', 'Runs one case: clear state, reset, build stimuli, launch the three together.'),
        ('max_cycles = 4000;', '<strong>멈추지 않게 하는 한도.</strong> 회로가 멈춰도 consumer 와 monitor 는 4000 사이클 뒤 끝난다. Part 1 Test 3 에서 배운 것이다.', '<strong>A limit so nothing hangs.</strong> Even if the circuit stalls, consumer and monitor stop after 4000 cycles. A lesson from Part 1\'s Test 3.'),
        ('fork', 'producer, consumer, monitor 를 동시에. <code>join</code> 은 셋 다 끝나길 기다린다.', 'Producer, consumer and monitor together; <code>join</code> waits for all three.'),
        ('if (out_count != N_ITEMS) begin', '규칙 4. <strong>80 개가 다 나와야 한다.</strong>', 'Rule 4: <strong>all 80 must come out.</strong>'),
        ('$display("RESULT %-14s', '결과 한 줄. 14 · 15 절의 표가 전부 이 줄에서 왔다. 사이클은 시간을 clock 주기 10 ns 로 나눈 것이다.', 'One result line; every table in sections 14 and 15 comes from it. Cycles are the time divided by the 10 ns clock period.'),
        ('if (selected("case9_skew"))', 'case 넷. 인자는 순서대로 skew, seed, 쓰기 on/period, 읽기 on/period. seed 는 고정이라 매번 같은 순서로 섞인다.', 'The four cases. Arguments in order: skew, seed, write on/period, read on/period. Seeds are fixed, so every run shuffles the same way.'),
        ('#500000;', '전체 watchdog. 무엇이 멈추든 0.5 ms 뒤에는 끝난다.', 'A global watchdog: whatever hangs, it all ends after 0.5 ms.'),
      ]),
]

P2TB_TREES = [
    (T('코드 윤곽', 'outline'), [
        N('tb_fifo_q', file='tbf', open=False, kids=[
            N('push · pop', file='tbf', at='task automatic push('),
            N('measure_empty_latency', file='tbf', at='task automatic measure_empty_latency;'),
            N('fill_and_drain', file='tbf', at='task automatic fill_and_drain;'),
            N('stream', file='tbf', at='task automatic stream;')]),
        N('tb_even_odd', file='tbe', kids=[
            N(T('예상값 queue · 측정 변수', 'expected queues · counters'), file='tbe', at='logic [DATA_WIDTH-1:0] exp_even [$];'),
            N(T('점유량 추적기', 'occupancy tracker'), file='tbe', at='if (dut.even_wr_en && !dut.even_full)'),
            N(T('추적 파일 (+TRACE)', 'trace file (+TRACE)'), file='tbe', at='int trace_cycle;'),
            N('build_stim', file='tbe', at='task automatic build_stim('),
            N('producer', file='tbe', at='task automatic producer('),
            N('consumer', file='tbe', at='task automatic consumer('),
            N(T('monitor · 규칙 넷', 'monitor · four rules'), file='tbe', at='task automatic monitor('),
            N('run_case', file='tbe', at='task automatic run_case('),
            N(T('case 넷', 'the four cases'), file='tbe', at='if (selected("case9_skew"))')])]),
]

# ════════════════════════════════════════════════════════════════ p2build

P2BUILD_FILES = [
    F(P2 + 'Makefile', role='t', key='mk2', label='part2/Makefile',
      sum=T('변수 셋이 전부다. <code>VARIANT</code> 가 FIFO 를, <code>DEPTH_*</code> 가 깊이를, <code>TEST</code> 가 case 를 고른다. 두 구현의 빌드 결과는 <code>build/sync</code> 와 <code>build/async</code> 로 갈라져서 서로 덮어쓰지 않는다.',
            'Three variables do it all: <code>VARIANT</code> picks the FIFO, <code>DEPTH_*</code> the depth, <code>TEST</code> the case. Builds land in <code>build/sync</code> and <code>build/async</code>, so neither overwrites the other.'),
      notes=[
        ('VARIANT ?= sync', '<code>?=</code> 는 "명령줄에서 안 줬을 때만" 이다. <code>make VARIANT=async run</code> 처럼 바꾼다.', '<code>?=</code> means "only if not given on the command line". Override it as in <code>make VARIANT=async run</code>.'),
        ('DEPTH        = $(DEPTH_$(VARIANT))', '<strong>변수 이름을 변수로 만든다.</strong> <code>VARIANT</code> 가 sync 면 <code>$(DEPTH_sync)</code>, 곧 40 이 된다. 아래 <code>SRC_</code> 도 같은 수법이다.', '<strong>A variable name built from a variable.</strong> With <code>VARIANT</code> = sync this is <code>$(DEPTH_sync)</code>, i.e. 40. <code>SRC_</code> below uses the same trick.'),
        ('PLUSARGS = +TEST=$(TEST)', '<code>TEST</code> 를 줬을 때만 plusarg 를 붙인다. 안 주면 testbench 가 case 넷을 다 돈다.', 'The plusarg is added only when <code>TEST</code> is given; without it the testbench runs all four cases.'),
        ('SRC_async = $(PART1)/fifo_if.sv', '<strong>Part 1 을 경로로 가져온다.</strong> 복사하지 않으므로 Part 1 을 고치면 Part 2 에 바로 반영된다. interface 가 맨 앞이고 wrapper 가 맨 뒤다.', '<strong>Part 1 is pulled in by path,</strong> not copied, so a fix there shows up here at once. The interface goes first and the wrapper last.'),
        ('+define+FIFO_DEPTH=$(DEPTH)', '깊이를 testbench 의 <code>`FIFO_DEPTH</code> 로 넘긴다. testbench 가 그걸 DUT 의 parameter 로 다시 넘긴다.', 'Hands the depth to the testbench\'s <code>`FIFO_DEPTH</code>, which passes it on to the DUT\'s parameter.'),
        ('tb_even_odd -Mdir=$(BUILD)/csrc -o $(BUILD)/simv', '<code>-Mdir</code> 은 중간 산출물, <code>-o</code> 는 실행 파일 위치다. variant 마다 다른 폴더다.', '<code>-Mdir</code> places the intermediate build, <code>-o</code> the executable: a separate folder per variant.'),
        ('fifo: $(BUILD)', '층 1 testbench 를 따로 굽고 돌린다. 실행 파일 이름도 <code>simv_fifo</code> 로 따로다.', 'Builds and runs the layer-1 testbench separately, with its own executable name, <code>simv_fifo</code>.'),
        ('compare:', '두 구현을 차례로 돌리고 결과 줄만 걸러 보여준다. 15 절 표가 이 출력이다.', 'Runs both variants in turn and filters to the result lines. Section 14\'s table is this output.'),
        ('printdepth:', '<code>compare</code> 가 각 variant 의 깊이를 물어볼 때 쓰는 보조 target.', 'A helper target <code>compare</code> uses to ask each variant its depth.'),
        ('trace: compile', 'CSV 를 <code>trace/</code> 에 모은다. 저장소의 <code>trace_sync/</code> 와 <code>trace_async/</code> 는 variant 별로 돌린 뒤 폴더 이름을 바꿔 둔 것이다.', 'Collects the CSVs into <code>trace/</code>. The repository\'s <code>trace_sync/</code> and <code>trace_async/</code> are that folder renamed after a run of each variant.'),
      ]),
]

# ════════════════════════════════════════════════════════════════ p2fix
# 14 절. 재는 쪽을 고친 커밋 셋.

P2FIX = [
    C('fc6647b',
      note=T('최대 점유량만으로는 두 구현이 안 갈렸다. <strong>걸린 시간</strong>을 재도록 했다.', 'Peak occupancy alone did not separate the two implementations, so the run <strong>time</strong> is now measured too.'),
      notes={TBE: [
          ('time start_time;', '시작과 마지막 출력 시각.', 'Start time and time of the last output.'),
          ('last_out_time = $time;', '값이 나올 때마다 덮어쓴다. 끝나면 마지막 출력의 시각이 남는다.', 'Overwritten on every output, so what remains is the last one\'s time.'),
          ('start_time = $time;', '자극을 만든 직후, 셋을 띄우기 직전.', 'Right after the stimuli are built, just before launching the three.'),
          ('(last_out_time - start_time) / 10,', 'ns 를 clock 주기 10 으로 나눠 사이클로.', 'ns divided by the 10 ns period, giving cycles.'),
      ]}),
    C('08fbbb3',
      note=T('점유량 추적기가 엣지 1 ns 뒤에 읽어서 <strong>다음 엣지의 꺼내기</strong>를 미리 셌다. 여덟 run 중 다섯의 최대 점유량이 틀렸다. 엣지 그 순간에 읽도록 <code>#1</code> 을 지웠다.',
             'The tracker read 1 ns after the edge and so counted <strong>the next edge\'s pop</strong> early; five of eight runs had the wrong peak. The <code>#1</code> is gone, so it reads at the edge itself.'),
      notes={TBE: [
          ('-#1;', '<strong>이 한 줄.</strong> 1 ns 뒤면 <code>Read_en</code> 이 아직 바뀌지 않았어도 <code>sel</code> 과 <code>even_rd_en</code> 은 이미 <strong>다음 엣지를 위한 값</strong>으로 바뀌어 있다.', '<strong>This one line.</strong> 1 ns later, <code>sel</code> and <code>even_rd_en</code> already hold <strong>the values meant for the next edge.</strong>'),
      ]}),
    C('d445cfc',
      note=T('정반대 버그. empty 지연을 엣지 순간에 읽어서 <strong>이번 엣지가 낸 결과</strong>를 한 번 늦게 봤다. 비동기 판이 3 대신 4 로 나왔다. 1 ns 기다리게 했다.',
             'The opposite bug: empty was read at the edge instant and so saw <strong>this edge\'s result</strong> one edge late, giving 4 instead of 3 for the async variant. Now it waits 1 ns.'),
      notes={TBF: [
          ('#1;', '<strong>이 한 줄.</strong> 이번엔 엣지의 결과를 봐야 하므로 NBA 가 끝난 뒤에 읽는다.', '<strong>This one line.</strong> Here we want the edge\'s result, so read after the non-blocking updates land.'),
      ]}),
]

# ════════════════════════════════════════════════════════════════ history
# 16 절. Lab 저장소의 lab1 커밋 전부. 주석만 바꾼 커밋은 요약만 남는다.

RENAMES = {P1 + 'async_fifo.sv': P1 + 'fifo1.v', P1 + 'fifo_mem.sv': P1 + 'fifomem.v',
           P1 + 'fifo_rptr.sv': P1 + 'rptr_empty.v', P1 + 'fifo_wptr.sv': P1 + 'wptr_full.v',
           P1 + 'sync_r2w.sv': P1 + 'sync_r2w.v', P1 + 'sync_w2r.sv': P1 + 'sync_w2r.v'}

HISTORY = [
    C('1c17c62', note=T('논문 코드 여섯 파일을 <strong>그대로</strong> 박았다. 이 뒤의 모든 diff 가 여기서 출발한다.', 'The paper\'s six files, <strong>verbatim.</strong> Every later diff starts here.')),
    C('eddacd9', renames=RENAMES, subject='Lab 1 Part 1: the work on top of the Cummings baseline',
      note=T('Part 1 의 본 작업. <code>.v</code> 여섯이 <code>.sv</code> 일곱이 되고 testbench 와 Makefile 이 생겼다. 파일마다의 해설은 04 절 뷰어에 있다. 이름이 바뀐 파일은 옛 이름과 비교해 보여준다.',
             'Part 1\'s main work: six <code>.v</code> files become seven <code>.sv</code>, plus the testbench and Makefile. Per-file commentary is in the section 04 viewer. Renamed files are diffed against their old names.')),
    C('000aff8', note=T('bash 용 <code>env.sh</code> 를 더했다. 나머지 파일은 머리 주석만 바뀌어서 주석을 빼면 차이가 없다.', 'Adds <code>env.sh</code> for bash. The other files changed only their header comments, so with comments stripped there is no difference.')),
    C('755a20f', note=P1FIX[0].note),
    C('ec8e782', note=P1FIX[1].note),
    C('e8ad3d8', note=T('Part 2 의 뼈대. <code>VARIANT</code> 로 FIFO 를 갈아끼우는 Makefile. 아직 RTL 은 없다.', 'Part 2\'s scaffold: a Makefile that swaps the FIFO by <code>VARIANT</code>. No RTL yet.')),
    C('ae053f3', note=T('<strong>비동기 wrapper 를 먼저</strong> 만들었다. 이미 검증된 Part 1 을 감싸면 층 1 testbench 를 먼저 검증할 수 있다. 동기 판은 그 testbench 로 나중에 검증한다.', 'The <strong>async wrapper came first.</strong> Wrapping the already-verified Part 1 let the layer-1 testbench be proven first; the sync FIFO was then checked against it.')),
    C('7dd0229', note=T('측정 기록만 (문서).', 'Measurements only (document).')),
    C('e50c499', note=T('동기 FIFO. 층 1 testbench 를 그대로 통과했다.', 'The synchronous FIFO; it passed the layer-1 testbench unchanged.')),
    C('a942c46', note=T('짝홀 교대 회로.', 'The even/odd alternating circuit.')),
    C('96d17ce', note=T('층 2 testbench 와 case 넷. 깊이를 <code>+define</code> 으로 넘기기 시작했다.', 'The layer-2 testbench and four cases; the depth starts arriving via <code>+define</code>.')),
    C('fc6647b', note=P2FIX[0].note),
    C('c5fb8e4', note=T('두 구현의 비교 결과 기록 (문서).', 'Records the comparison of both implementations (document).')),
    C('81a28ce', note=T('문서의 줄 수 하나 정정.', 'One line count corrected in a document.')),
    C('deecd1e', note=T('사이클마다 CSV 를 남기는 <code>+TRACE</code>. 이 추적이 14 절의 버그 둘을 드러냈다.', '<code>+TRACE</code>, one CSV row per cycle. This trace is what exposed the two bugs in section 14.')),
    C('ae63333', only=(), note=T('Test 2 를 고친 가지 (<code>755a20f</code>, <code>ec8e782</code>) 를 합친 merge. 바뀐 내용은 그 두 커밋에 있다.', 'Merges the branch that fixed Test 2 (<code>755a20f</code>, <code>ec8e782</code>); the changes are in those two commits.')),
    C('d2d6692', note=T('Part 1 에도 <code>+TRACE</code>. clock 이 둘이라 1 ns 격자로 찍는다.', '<code>+TRACE</code> for Part 1 too, on a 1 ns grid since there are two clocks.')),
    C('7f4de18', note=T('추적 CSV 를 저장소에 넣었다 (데이터).', 'Commits the trace CSVs (data).')),
    C('08fbbb3', note=P2FIX[1].note),
    C('486e745', note=T('추적기를 고친 뒤 다시 찍은 CSV (데이터).', 'The CSVs re-taken after the tracker fix (data).')),
    C('2ea6fb3', note=T('틀렸던 최대 점유량을 문서에서 정정.', 'Corrects the wrong peak occupancies in the document.')),
    C('d445cfc', note=P2FIX[2].note),
    C('b8908a2', note=T('empty 지연을 다시 잰 결과 (데이터).', 'The re-measured empty latency (data).')),
    C('4f0761b', note=T('"4" 에 붙어 있던 설명을 "3" 으로 고쳤다. 코드에서는 주석만 바뀌었다.', 'Rewrites the explanation that had been attached to "4" so it says 3. In the code only comments changed.')),
    C('c45c13a', note=T('<strong>코드의 주석을 전부 뺐다.</strong> 설명은 이 페이지가 맡는다. 주석과 공백을 뺀 토큰 열이 앞뒤로 같은 것을 확인했으므로 동작은 같다. 이 뷰어는 모든 diff 에서 주석을 빼고 비교하므로 이 커밋은 비어 보인다.', '<strong>Strips every comment from the code;</strong> this page carries the explanation. The token streams without comments and whitespace are identical before and after, so behaviour is unchanged. Every diff here compares with comments stripped, so this commit shows as empty.')),
]
