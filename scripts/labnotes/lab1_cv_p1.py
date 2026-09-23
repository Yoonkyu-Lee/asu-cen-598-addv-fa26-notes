# -*- coding: utf-8 -*-
"""Lab 1 코드 뷰어 · Part 1. 설명 카드는 그 줄에 든 글자로 붙는다 (codeview_build 참조)."""
from codeview_build import F, N, T

BASE = '1c17c62'       # Cummings 논문 코드 그대로 박은 첫 커밋
P1 = 'lab1/part1/'

# ════════════════════════════════════════════════════════════════ given
# 02 절. 주어진 것. 논문 코드를 주석까지 원문 그대로 보여준다.

GIVEN_FILES = [
    F(P1 + 'fifo1.v', rev=BASE, strip=False, label='fifo1.v', key='fifo1',
      sum=T('최상위. 나머지 다섯을 묶는 배선뿐이고 로직은 없다. <strong>포인터 네 가닥과 주소 두 가닥</strong>이 모듈 사이를 오가는 것이 전부다.',
            'Top level. Pure wiring for the other five, no logic. All that crosses between modules is <strong>four pointers and two addresses.</strong>'),
      notes=[
        ('module fifo1', 'parameter 가 둘이다. <code>DSIZE</code> 는 데이터 폭, <code>ASIZE</code> 는 주소 비트 수다. <strong>깊이는 직접 주지 않고 2<sup>ASIZE</sup> 로 정해진다.</strong> 처음부터 2 의 거듭제곱만 만들 수 있게 짠 것이다.',
         'Two parameters: <code>DSIZE</code> is the data width, <code>ASIZE</code> the address bits. <strong>Depth is not given directly; it is 2<sup>ASIZE</sup>.</strong> The design can only ever be a power of two.'),
        ('input              winc, wclk, wrst_n', '쓰기 쪽과 읽기 쪽이 <strong>clock 도 reset 도 따로</strong>다. reset 을 영역마다 두는 이유는 각 영역의 flip-flop 이 자기 clock 기준으로 reset 에서 풀려나야 하기 때문이다 (4 강).',
         'The write and read sides have <strong>separate clocks and separate resets.</strong> Each domain\'s flops have to come out of reset relative to their own clock (Lecture 4).'),
        ('wire [ASIZE-1:0] waddr, raddr;', '<strong>주소는 ASIZE 비트, 포인터는 ASIZE+1 비트.</strong> 한 비트 더 있는 것이 5 강의 wrap bit 다. 주소로 쓸 때는 떼고, full 과 empty 를 가를 때만 쓴다. 이름 규칙도 있다. <code>wq2_rptr</code> 는 "읽기 포인터를 쓰기 영역으로 동기화한 2 단째" 다. 앞 글자가 도착한 영역이다.',
         '<strong>Addresses are ASIZE bits, pointers ASIZE+1.</strong> The extra bit is Lecture 5\'s wrap bit: dropped for addressing, used only to tell full from empty. Naming has a rule too: <code>wq2_rptr</code> is "the read pointer, second sync stage, in the write domain". The leading letter is the domain it lands in.'),
        ('fifomem #(DSIZE, ASIZE) fifomem', '메모리의 쓰기 enable 에 <code>winc</code> 를 그대로 물리고 <code>wfull</code> 을 따로 넘긴다. 가득 찼을 때 쓰기를 막는 일은 <strong>메모리 안에서</strong> 한다.',
         'The memory gets <code>winc</code> straight as its write enable and <code>wfull</code> alongside. Blocking writes when full happens <strong>inside the memory.</strong>'),
      ]),
    F(P1 + 'fifomem.v', rev=BASE, strip=False, label='fifomem.v', key='fifomem',
      sum=T('저장소. 쓰기는 <code>wclk</code> 로, 읽기는 clock 없이 조합으로 한다.', 'The storage. Writes happen on <code>wclk</code>; reads are combinational, no clock at all.'),
      notes=[
        ('`ifdef VENDORRAM', '합성할 때는 벤더의 dual-port RAM 매크로로 갈아끼울 수 있게 해뒀다. 정의하지 않으면 아래 RTL 모델이 쓰인다. Lab 에서는 이 분기를 안 쓴다.',
         'For synthesis you can swap in a vendor dual-port RAM macro. Leave the macro undefined and the RTL model below is used. The lab never takes this branch.'),
        ('assign rdata = mem[raddr];', '<strong>읽기에 clock 이 없다.</strong> <code>raddr</code> 가 가리키는 칸이 늘 <code>rdata</code> 에 나와 있다. 그래서 "머리에 있는 값을 먼저 보고, <code>rinc</code> 로 꺼낸다" 는 쓰임새가 된다. Part 2 의 <code>fifo_q</code> 계약이 이 모양을 그대로 따랐다.',
         '<strong>The read has no clock.</strong> Whatever <code>raddr</code> points at is always on <code>rdata</code>, so you look at the head first and pop it with <code>rinc</code>. Part 2\'s <code>fifo_q</code> contract copies this shape.'),
        ('if (wclken && !wfull)', '가득 찼는데 들어온 쓰기는 여기서 버려진다. 포인터 쪽도 같은 조건으로 멈추므로 둘이 어긋나지 않는다.',
         'A write that arrives when full is dropped here. The pointer stops under the same condition, so the two never disagree.'),
      ]),
    F(P1 + 'sync_w2r.v', rev=BASE, strip=False, label='sync_w2r.v', key='sync_w2r',
      sum=T('쓰기 포인터를 읽기 영역으로 넘기는 2 단 동기화기.', 'Two-stage synchroniser carrying the write pointer into the read domain.'),
      notes=[
        ('always @(posedge rclk', '<strong>받는 쪽 clock (<code>rclk</code>) 으로 돈다.</strong> 동기화기는 보내는 쪽이 아니라 받는 쪽 영역에 속한다.',
         '<strong>It runs on the receiving clock, <code>rclk</code>.</strong> A synchroniser belongs to the domain that receives, not the one that sends.'),
        ('{rq2_wptr,rq1_wptr} <= {rq1_wptr,wptr};', 'flip-flop 두 개를 한 줄에 썼다. 오른쪽을 먼저 다 읽고 한꺼번에 쓰므로 <code>rq1</code> 은 <code>wptr</code> 를, <code>rq2</code> 는 <strong>옛</strong> <code>rq1</code> 을 받는다. 두 칸짜리 shift register 다.',
         'Two flops in one line. The right-hand side is read first and all written at once, so <code>rq1</code> takes <code>wptr</code> and <code>rq2</code> takes the <strong>old</strong> <code>rq1</code>: a two-stage shift register.'),
      ]),
    F(P1 + 'sync_r2w.v', rev=BASE, strip=False, label='sync_r2w.v', key='sync_r2w',
      sum=T('읽기 포인터를 쓰기 영역으로 넘긴다. <code>sync_w2r</code> 의 거울상이고 <code>wclk</code> 로 돈다.', 'Carries the read pointer into the write domain. The mirror of <code>sync_w2r</code>, clocked by <code>wclk</code>.')),
    F(P1 + 'rptr_empty.v', rev=BASE, strip=False, label='rptr_empty.v', key='rptr_empty',
      sum=T('읽기 포인터와 <code>rempty</code>. 이 파일에 이 설계의 요령이 다 들어 있다.', 'The read pointer and <code>rempty</code>. Every trick in the design is in this file.'),
      notes=[
        ('reg  [ADDRSIZE:0] rbin;', '포인터를 <strong>두 벌</strong> 둔다. binary <code>rbin</code> 은 더하기와 메모리 주소에 쓰고, gray <code>rptr</code> 는 상대 영역으로 건너보낼 때만 쓴다. 논문은 이 방식을 "GRAYSTYLE2" 라고 부른다.',
         'The pointer is kept <strong>twice</strong>: binary <code>rbin</code> for incrementing and addressing, gray <code>rptr</code> only for sending across. The paper calls this style "GRAYSTYLE2".'),
        ('{rbin, rptr} <= {rbinnext, rgraynext};', '두 벌을 같은 엣지에 같이 갱신한다. 그래서 gray 쪽이 binary 쪽을 늘 정확히 따라간다.',
         'Both copies update on the same edge, so the gray one always tracks the binary one exactly.'),
        ('assign raddr     = rbin[ADDRSIZE-1:0];', '주소는 binary 의 아래 비트만 쓴다. 맨 위 wrap bit 는 뗀다.',
         'The address is the binary pointer\'s low bits, with the top wrap bit dropped.'),
        ('assign rbinnext  = rbin + (rinc & ~rempty);', '읽기 요청이 있고 비어 있지 않을 때만 한 칸 간다. 비었는데 읽으라고 해도 무시된다.',
         'It advances only when a read is requested and the FIFO is not empty. A read on empty is ignored.'),
        ('assign rgraynext = (rbinnext>>1) ^ rbinnext;', 'binary 를 gray 로. 한 칸 오른쪽으로 민 것과 XOR 하면 이웃한 값끼리 한 비트만 다르게 된다.',
         'Binary to gray: XOR with itself shifted right once, and neighbouring values differ in exactly one bit.'),
        ('assign rempty_val = (rgraynext == rq2_wptr);', '<strong>다음 포인터</strong>로 비교한다. 지금 포인터가 아니다. 이렇게 하면 <code>rempty</code> 를 등록해도 한 사이클 늦지 않는다. 선언 없이 쓰인 <code>rempty_val</code> 은 Verilog-2001 의 implicit wire 다.',
         'The comparison uses the <strong>next</strong> pointer, not the current one, so registering <code>rempty</code> does not make it a cycle late. <code>rempty_val</code>, used without a declaration, is a Verilog-2001 implicit wire.'),
        ('if (!rrst_n) rempty <= 1\'b1;', '<code>rempty</code> 는 등록된 출력이고 reset 값은 1 이다. 빈 채로 시작한다. 이 등록 한 단이 03 절 레지스터 넷 중 마지막이다.',
         '<code>rempty</code> is a registered output that resets to 1: it starts empty. This one register is the last of section 03\'s four.'),
      ]),
    F(P1 + 'wptr_full.v', rev=BASE, strip=False, label='wptr_full.v', key='wptr_full',
      sum=T('쓰기 포인터와 <code>wfull</code>. 구조는 <code>rptr_empty</code> 와 같고 full 판정만 다르다.', 'The write pointer and <code>wfull</code>. Same structure as <code>rptr_empty</code>; only the full test differs.'),
      notes=[
        ('// Simplified version of the three necessary full-tests:', '<strong>gray code 로 full 을 가리는 법.</strong> 쓰기 포인터가 읽기 포인터를 한 바퀴 따라잡았을 때가 full 이다. binary 라면 MSB 만 다르고 나머지가 같다. 그런데 gray 로 바꾸면 <strong>위 두 비트가 반전되고 나머지가 같은</strong> 모양이 된다. 주석이 세 조건을 풀어 쓰고, 아래 한 줄이 그걸 합쳤다.',
         '<strong>How to detect full in gray code.</strong> Full is when the write pointer has lapped the read pointer. In binary that means only the MSB differs. In gray code it becomes <strong>the top two bits inverted and the rest equal.</strong> The comment spells out the three conditions; the line below merges them.'),
        ('assign wfull_val = (wgraynext=={~wq2_rptr[ADDRSIZE:ADDRSIZE-1],', '위 두 비트를 뒤집은 동기화된 읽기 포인터와 <strong>다음</strong> 쓰기 포인터를 비교한다. empty 쪽과 같은 이유로 다음 포인터를 쓴다.',
         'The <strong>next</strong> write pointer is compared with the synchronised read pointer, top two bits inverted. The next pointer, for the same reason as on the empty side.'),
      ]),
]

GIVEN_TREES = [
    (T('파일', 'files'), [
        N('Cummings SNUG2002 · style #1', kids=[
            N('fifo1.v', file='fifo1'), N('fifomem.v', file='fifomem'),
            N('sync_w2r.v', file='sync_w2r'), N('sync_r2w.v', file='sync_r2w'),
            N('rptr_empty.v', file='rptr_empty'), N('wptr_full.v', file='wptr_full')])]),
    (T('모듈 계층', 'module hierarchy'), [
        N('fifo1', file='fifo1', kids=[
            N('fifomem  (storage)', file='fifomem'),
            N('rptr_empty  (rclk)', file='rptr_empty'),
            N('wptr_full  (wclk)', file='wptr_full'),
            N('sync_w2r  (rclk)', file='sync_w2r'),
            N('sync_r2w  (wclk)', file='sync_r2w')])]),
]

# ════════════════════════════════════════════════════════════════ p1
# 04 절. 논문 코드 (주석 뺌) → 제출본. 파일마다 diff.

P1_FILES = [
    F(P1 + 'async_fifo.sv', base=BASE, base_path=P1 + 'fifo1.v', prov='lift', key='async_fifo',
      sum=T('<code>fifo1.v</code> 를 옮긴 최상위. 배선이라는 역할은 같고 <strong>연결 방식</strong>이 바뀌었다. 이름 연결 대신 <code>.*</code>, 메모리는 interface 로.',
            'The top level carried over from <code>fifo1.v</code>. Still just wiring, but <strong>how it connects</strong> changed: <code>.*</code> instead of named connections, and an interface to the memory.'),
      notes=[
        ('module async_fifo #(', 'parameter 가 <code>DSIZE / ASIZE</code> 에서 <code>DATA_WIDTH / DEPTH</code> 로 바뀌었다. 요구사항이 "data width 와 depth 로 parameterize" 를 말하므로 <strong>깊이를 직접 받는다.</strong> 타입도 <code>int</code> 로 못박았다.',
         'Parameters go from <code>DSIZE / ASIZE</code> to <code>DATA_WIDTH / DEPTH</code>. The requirement says "parameterised for width and depth", so <strong>depth is taken directly</strong>, typed as <code>int</code>.'),
        ('output logic                  almost_full,', '새 출력 둘. 요구사항의 3/4 플래그다. 논문에는 없다.', 'Two new outputs: the 3/4 flags the requirement asks for. The paper has none.'),
        ('localparam int ADDR_WIDTH = $clog2(DEPTH);', '주소 폭을 깊이에서 거꾸로 구한다. <strong>함정이 하나 있다.</strong> <code>DEPTH = 10</code> 을 주면 <code>$clog2</code> 가 4 로 올려서 실제로는 16 칸짜리가 만들어지고, 하위 모듈의 문턱도 16 기준으로 잡힌다. <strong>막는 검사가 없다.</strong> 2 의 거듭제곱만 넣어야 한다.',
         'The address width is derived back from the depth. <strong>One trap:</strong> give <code>DEPTH = 10</code> and <code>$clog2</code> rounds up to 4, so a 16-entry FIFO is built and the submodules set their thresholds for 16. <strong>Nothing checks this.</strong> Only powers of two belong here.'),
        ('logic [ADDR_WIDTH:0] wptr;', '논문의 <code>wire</code> 들이 <code>logic</code> 이 됐다. <strong>이름은 하나도 안 바꿨다.</strong> 하위 모듈의 포트 이름과 글자까지 같아야 아래 <code>.*</code> 가 붙기 때문이다.',
         'The paper\'s <code>wire</code>s become <code>logic</code>. <strong>Not one name changed.</strong> They have to match the child port names letter for letter, or the <code>.*</code> below cannot connect.'),
        ('fifo_if #(', '메모리로 가는 interface 를 하나 만든다. <strong>인스턴스 이름이 <code>mem_if</code> 인 것이 중요하다.</strong> <code>fifo_mem</code> 의 포트 이름도 <code>mem_if</code> 라서 아래 <code>fifo_mem</code> 도 <code>.*</code> 로 붙는다.',
         'One interface instance for the memory. <strong>That it is named <code>mem_if</code> matters:</strong> <code>fifo_mem</code>\'s port is also named <code>mem_if</code>, so <code>fifo_mem</code> too connects with <code>.*</code>.'),
        ('assign mem_if.wdata  = wdata;', 'interface 안의 신호를 최상위의 선으로 채운다. <code>wclken</code> 에 <code>winc</code> 를 물리는 것은 논문과 같다. <code>rdata</code> 만 반대 방향이다.',
         'The interface signals are driven from top-level nets. Tying <code>wclken</code> to <code>winc</code> is as in the paper. Only <code>rdata</code> flows the other way.'),
        ('sync_r2w #(', '<strong><code>.*</code> 는 포트마다 같은 이름의 신호를 찾아 붙인다.</strong> 이름이 하나라도 없으면 VCS 가 에러를 낸다. 그래서 틀려도 조용히 넘어가지 않는다. 대신 이름을 맞추는 부담이 선언 쪽으로 넘어간다. 인스턴스 다섯 개가 전부 이렇게 붙는다.',
         '<strong><code>.*</code> connects each port to the signal of the same name.</strong> If a name is missing, VCS errors out, so a mistake is never silent. The cost moves to the declarations, which must match. All five instances connect this way.'),
      ]),
    F(P1 + 'fifo_if.sv', base=BASE, base_path=P1 + 'fifo_if.sv', prov='add', key='fifo_if',
      sum=T('<strong>새 파일.</strong> 요구사항 "interface 와 modport 를 FIFO 나 메모리에 쓸 것" 을 메모리 쪽으로 채웠다.', '<strong>New file.</strong> It meets "use an interface and modport in the FIFO or memory" on the memory side.'),
      notes=[
        ('interface fifo_if #(', 'parameter 는 메모리와 같은 둘이다. 폭이 인스턴스마다 달라질 수 있게.', 'The same two parameters as the memory, so widths can vary per instance.'),
        ('logic [DATA_WIDTH-1:0] wdata;', '메모리가 만지는 신호를 전부 한 묶음에 넣었다. 쓰기 데이터·주소·clock·enable·<code>wfull</code>, 그리고 읽기 주소와 데이터. <strong><code>rclk</code> 은 없다.</strong> 읽기가 조합이라 필요 없다.',
         'Every signal the memory touches, in one bundle: write data, address, clock, enable, <code>wfull</code>, plus read address and data. <strong>There is no <code>rclk</code>:</strong> the read is combinational, so none is needed.'),
        ('modport mem (', '메모리가 보는 방향. <code>rdata</code> 만 output 이고 나머지는 input 이다. 방향을 여기 적어두면 메모리가 입력을 몰래 구동하는 실수를 컴파일러가 잡는다. <strong>modport 는 이것 하나뿐이다.</strong> 최상위는 modport 없이 <code>assign</code> 으로 채운다.',
         'The memory\'s view: <code>rdata</code> is the only output. With directions written here, the compiler catches the memory driving an input by mistake. <strong>This is the only modport;</strong> the top level fills the interface with plain <code>assign</code>s.'),
      ]),
    F(P1 + 'fifo_mem.sv', base=BASE, base_path=P1 + 'fifomem.v', prov='lift', key='fifo_mem',
      sum=T('<code>fifomem.v</code> 를 옮긴 것. <strong>동작은 한 줄도 안 바뀌었다.</strong> 포트 목록이 interface 하나로 줄어서 파일이 오히려 짧아졌다.', 'Carried over from <code>fifomem.v</code>. <strong>Behaviour unchanged, line for line.</strong> The port list collapses into one interface, so the file actually got shorter.'),
      notes=[
        ('fifo_if.mem mem_if', '포트가 이것 하나다. <code>fifo_if</code> 의 <code>mem</code> modport 로 받는다. 신호는 전부 <code>mem_if.</code> 를 앞에 붙여 쓴다.', 'A single port, taken through <code>fifo_if</code>\'s <code>mem</code> modport. Every signal is referred to as <code>mem_if.</code>something.'),
        ('assign mem_if.rdata = mem[mem_if.raddr];', '<code>VENDORRAM</code> 분기가 사라졌다. 남은 RTL 모델은 논문과 같다. 읽기는 여전히 조합이다.', 'The <code>VENDORRAM</code> branch is gone. The RTL model that remains matches the paper; the read is still combinational.'),
        ('always_ff @(posedge mem_if.wclk) begin', '<code>always</code> 가 <code>always_ff</code> 로. 요구사항이다. <code>always_ff</code> 는 안에 조합 논리를 잘못 쓰면 도구가 경고해준다는 점에서 그냥 <code>always</code> 보다 안전하다.', '<code>always</code> becomes <code>always_ff</code>, as required. It is also safer: tools warn if what is inside is not actually sequential.'),
      ]),
    F(P1 + 'sync_w2r.sv', base=BASE, base_path=P1 + 'sync_w2r.v', prov='lift', key='sync_w2r',
      sum=T('동작은 같다. 한 줄에 몰아 쓴 flip-flop 두 개를 두 줄로 풀었다.', 'Same behaviour. The two flops written on one line are spelled out on two.'),
      notes=[
        ('always_ff @(posedge rclk or negedge rrst_n) begin', '여전히 <code>rclk</code> 으로 돈다. reset 은 비동기로 걸린다 (<code>negedge rrst_n</code>).', 'Still clocked by <code>rclk</code>, with an asynchronous reset (<code>negedge rrst_n</code>).'),
        ('rq1_wptr <= wptr;', '1 단. <code>wptr</code> 를 처음 받는 flip-flop 이다. 여기서 metastability 가 생길 수 있다.', 'Stage one, the first flop to see <code>wptr</code>. This is where metastability can occur.'),
        ('rq2_wptr <= rq1_wptr;', '2 단. 1 단이 한 주기 동안 가라앉은 값을 받는다. 나머지 회로는 이 출력만 본다.', 'Stage two takes stage one after it has had a full cycle to settle. The rest of the circuit only ever sees this one.'),
      ]),
    F(P1 + 'sync_r2w.sv', base=BASE, base_path=P1 + 'sync_r2w.v', prov='lift', key='sync_r2w',
      sum=T('<code>sync_w2r</code> 과 같은 변경. <code>wclk</code> 으로 돈다.', 'The same change as <code>sync_w2r</code>, clocked by <code>wclk</code>.')),
    F(P1 + 'fifo_rptr.sv', base=BASE, base_path=P1 + 'rptr_empty.v', prov='extend', key='fifo_rptr',
      sum=T('<code>rptr_empty.v</code> 에 <strong>설계를 얹었다.</strong> <code>almost_empty</code> 를 내려면 점유량을 세야 해서 gray 를 binary 로 되돌리는 계산이 붙었다.', '<code>rptr_empty.v</code> <strong>with design added.</strong> Producing <code>almost_empty</code> needs an occupancy count, which means turning gray back into binary.'),
      notes=[
        ('output logic                  almost_empty,', '새 출력.', 'The new output.'),
        ('localparam int ALMOST_EMPTY_LEVEL = DEPTH / 4;', '"3/4 비었다" 는 "1/4 이하로 찼다" 다. 깊이 16 이면 4 개 이하.', '"Three quarters empty" means "at most a quarter full": 4 or fewer at depth 16.'),
        ('logic [ADDR_WIDTH:0] rq2_wbin;', '새 신호 둘. 건너온 쓰기 포인터의 binary 판과 점유량이다.', 'Two new signals: the binary form of the write pointer that crossed over, and the occupancy.'),
        ('function automatic logic [ADDR_WIDTH:0] gray2bin(', 'gray 를 binary 로 되돌린다. 맨 위 비트는 그대로, 그 아래는 <strong>바로 위의 binary 비트와 XOR</strong> 한다. 위에서 아래로 차례로 풀린다. <code>automatic</code> 이라 호출마다 지역 변수가 따로 잡힌다.',
         'Gray back to binary. The top bit copies across; each bit below is <strong>XORed with the binary bit just above it</strong>, unwinding top-down. <code>automatic</code> gives every call its own locals.'),
        ('rbinnext = rbin + (rinc && !rempty);', '논문의 <code>assign</code> 들이 <code>always_comb</code> 안으로 들어왔다. <code>&amp; ~</code> 가 <code>&amp;&amp; !</code> 로 바뀌었는데 1 비트라 결과는 같다.', 'The paper\'s <code>assign</code>s move into <code>always_comb</code>. <code>&amp; ~</code> becomes <code>&amp;&amp; !</code>; on single bits the result is identical.'),
        ('rq2_wbin = gray2bin(rq2_wptr);', '건너온 쓰기 포인터를 binary 로. gray 는 뺄셈이 안 되기 때문이다.', 'The write pointer that crossed over, back into binary, because gray code cannot be subtracted.'),
        ('rused_next = rq2_wbin - rbinnext;', '<strong>읽기 쪽이 보는 점유량</strong>, 그것도 이번 엣지 뒤의 값이다. 포인터가 한 비트 넓어서 한 바퀴 돌아도 뺄셈이 맞게 나온다. 쓰기 포인터는 늦게 건너오므로 이 값은 실제보다 <strong>작게</strong> 나온다. 그러면 <code>almost_empty</code> 는 일찍 서는 쪽으로 틀린다. 안전한 방향이다.',
         '<strong>Occupancy as the read side sees it</strong>, after this edge. The extra pointer bit keeps the subtraction right across a wrap. The write pointer arrives late, so this reads <strong>low</strong>, and <code>almost_empty</code> errs towards asserting early: the safe direction.'),
        ('almost_empty_val =', '4 개 이하면 선다. 비었을 때도 선다.', 'Asserts at 4 or fewer, including when empty.'),
        ('always_ff @(posedge rclk or negedge rrst_n) begin', '레지스터 넷을 한 블록에서 갱신한다. <code>almost_empty</code> 도 등록된 출력이고 reset 값이 1 이다. 비어서 시작하니까.', 'All four registers update in one block. <code>almost_empty</code> is registered too and resets to 1, since the FIFO starts empty.'),
      ]),
    F(P1 + 'fifo_wptr.sv', base=BASE, base_path=P1 + 'wptr_full.v', prov='extend', key='fifo_wptr',
      sum=T('<code>wptr_full.v</code> 에 같은 방식으로 <code>almost_full</code> 을 얹었다.', '<code>almost_full</code> added to <code>wptr_full.v</code> the same way.'),
      notes=[
        ('localparam int ALMOST_FULL_LEVEL = (3 * DEPTH) / 4;', '16 의 3/4, 12 개. 곱하고 나서 나눠야 한다. <code>DEPTH / 4 * 3</code> 도 여기선 같지만 순서가 습관이 되면 좋다.', '3/4 of 16 is 12. Multiply before dividing; <code>DEPTH / 4 * 3</code> happens to match here, but the habit is worth keeping.'),
        ('function automatic logic [ADDR_WIDTH:0] gray2bin(', '<code>fifo_rptr</code> 와 <strong>똑같은 함수가 복사돼 있다.</strong> package 로 빼면 한 곳에서 고칠 수 있다. 지금은 두 곳을 같이 고쳐야 한다.', '<strong>The same function, copied</strong> from <code>fifo_rptr</code>. A package would let it be fixed in one place; as it stands, both copies must change together.'),
        ('wused_next = wbinnext - wq2_rbin;', '쓰기 쪽이 보는 점유량. 읽기 포인터가 늦게 건너오므로 실제보다 <strong>크게</strong> 나온다. <code>almost_full</code> 은 일찍 서는 쪽으로 틀린다. 역시 안전한 방향이다.', 'Occupancy as the write side sees it. The read pointer arrives late, so this reads <strong>high</strong> and <code>almost_full</code> errs early: again the safe way.'),
        ('wfull_val =', 'full 판정은 논문과 같다. 한 줄을 세 줄로 나눴을 뿐이다.', 'The full test is the paper\'s, split over three lines.'),
        ('almost_full_val =', '12 개 이상이면 선다. <strong>다음</strong> 점유량으로 판정하고 등록하므로, 12 번째 쓰기가 실리는 바로 그 엣지 뒤에 선다 (08 절 파형의 마커 3).', 'Asserts at 12 or more. It is judged on the <strong>next</strong> occupancy and registered, so it rises right after the edge that lands the 12th write (marker 3 in section 08).'),
      ]),
]

P1_TREES = [
    (T('파일', 'files'), [
        N('part1  RTL', kids=[
            N('async_fifo.sv', file='async_fifo', badge='← fifo1.v'),
            N('fifo_if.sv', file='fifo_if', badge=T('새로', 'new')),
            N('fifo_mem.sv', file='fifo_mem', badge='← fifomem.v'),
            N('fifo_rptr.sv', file='fifo_rptr', badge='← rptr_empty.v'),
            N('fifo_wptr.sv', file='fifo_wptr', badge='← wptr_full.v'),
            N('sync_w2r.sv', file='sync_w2r'),
            N('sync_r2w.sv', file='sync_r2w')])]),
    (T('모듈 계층', 'module hierarchy'), [
        N('async_fifo', file='async_fifo', kids=[
            N('mem_if : fifo_if', file='fifo_if'),
            N('fifo_mem  (mem_if.mem)', file='fifo_mem'),
            N('fifo_rptr  (rclk)', file='fifo_rptr'),
            N('fifo_wptr  (wclk)', file='fifo_wptr'),
            N('sync_w2r  (rclk)', file='sync_w2r'),
            N('sync_r2w  (wclk)', file='sync_r2w')])]),
]

# ════════════════════════════════════════════════════════════════ p1tb
# 05 절. testbench 전문.

TB1 = P1 + 'tb_async_fifo.sv'
P1TB_FILES = [
    F(TB1, role='v', key='tb', label='part1/tb_async_fifo.sv',
      sum=T('테스트 셋을 실행 파일 하나에 넣고 plusarg 로 고른다. 공용 task 넷 (reset, 쓰기 한 번, 읽기 한 번, 추적) 위에 테스트 셋이 올라간다.', 'Three tests in one executable, picked by plusarg. They sit on top of shared helpers: reset, one write, one read, and the trace.'),
      notes=[
        ('localparam int AF_LEVEL', '문턱을 <strong>설계와 같은 식</strong>으로 적었다. 깊이를 바꾸면 설계와 testbench 가 같이 따라간다. 숫자 12 를 박아두면 조용히 갈라진다.', 'The thresholds are written <strong>the way the design writes them</strong>, so both follow a depth change together. Hard-coding 12 would let them drift apart silently.'),
        ('logic [DATA_WIDTH-1:0] wdata;', '신호 이름을 DUT 포트와 글자까지 같게 선언했다. 그래야 아래 <code>.*</code> 한 줄로 DUT 가 붙는다.', 'Signals named exactly like the DUT ports, so the <code>.*</code> below hooks the DUT up in one line.'),
        ('forever #5 wclk = ~wclk;', '쓰기 clock 10 ns.', 'Write clock, 10 ns.'),
        ('forever #7 rclk = ~rclk;', '읽기 clock 14 ns. <strong>10 과 14 는 정수배가 아니라</strong> 두 clock 의 엣지 간격이 매번 달라진다. CDC 를 여러 위상에서 두드리게 된다.', 'Read clock, 14 ns. <strong>10 and 14 are not integer multiples</strong>, so the gap between the two clocks\' edges keeps shifting and the crossing gets exercised at many phases.'),
        ('$fsdbDumpfile("novas.fsdb");', 'Verdi 로 볼 파형을 전부 쏟는다.', 'Dump everything for Verdi.'),
        ('int    trace_fd;', '이 페이지 파형이 여기서 나왔다. <code>+TRACE</code> 를 줄 때만 파일을 연다. clock 이 둘이라 공통으로 삼을 clock 이 없어서 <strong>1 ns 격자</strong>로 찍는다. 두 clock 의 모든 엣지에 정확히 걸린다.', 'This page\'s waveforms come from here. The file opens only on <code>+TRACE</code>. With two clocks there is no common one to sample on, so it samples a <strong>1 ns grid</strong>, which lands on every edge of both.'),
        ('task automatic reset_fifo;', 'reset 을 둘 다 내리고, <strong>각 clock 으로 세 엣지씩</strong> 기다렸다가, 각자 자기 clock 의 negedge 에서 푼다. 엣지 한가운데서 풀면 recovery 위반이 된다 (4 강).', 'Both resets go low, wait <strong>three edges of each clock</strong>, then release, each on its own clock\'s negedge. Releasing right on an edge would violate recovery time (Lecture 4).'),
        ('task automatic write_word(', '쓰기 한 번. <code>wfull</code> 이 풀리길 기다렸다가 negedge 에 데이터와 <code>winc</code> 를 올리고 한 주기 뒤 내린다. 입력을 negedge 에 바꿔서 posedge 에서 잡히는 순간과 겹치지 않게 한다.', 'One write. Wait for <code>wfull</code> to clear, raise data and <code>winc</code> on a negedge, drop them a cycle later. Changing inputs on the negedge keeps them clear of the posedge that captures them.'),
        ('task automatic read_word(', '읽기 한 번. <strong><code>rdata</code> 를 먼저 읽고 <code>rinc</code> 를 올린다.</strong> 메모리 읽기가 조합이라 머리 값이 이미 나와 있다. <code>rinc</code> 는 그걸 꺼내는 신호다.', 'One read. <strong>Take <code>rdata</code> first, then raise <code>rinc</code>.</strong> The memory read is combinational, so the head is already there; <code>rinc</code> is what removes it.'),
        ('task automatic test_fill_empty;', 'Test 1. reset 직후 비었는지, 16 개를 넣으면 <code>wfull</code> 이 서는지, 16 개를 빼면 넣은 순서대로 나오는지.', 'Test 1: empty after reset, <code>wfull</code> after 16 writes, and 16 reads in the order written.'),
        ('wait (wfull);', '약한 곳이 하나 있다. <code>wfull</code> 이 <strong>너무 일찍</strong> 서면 <code>write_word</code> 가 <code>wait (!wfull)</code> 에서 영영 기다린다. 실패가 에러가 아니라 <strong>멈춤</strong>으로 나타난다.', 'One weak spot: if <code>wfull</code> rose <strong>too early</strong>, <code>write_word</code> would wait forever on <code>wait (!wfull)</code>. The failure would show up as a <strong>hang</strong>, not an error.'),
        ('if (read_value !== i[DATA_WIDTH-1:0]) begin', '<code>!==</code> 는 X 와 Z 까지 비교한다. <code>!=</code> 를 쓰면 X 가 섞였을 때 결과가 X 가 되어 if 가 그냥 넘어간다.', '<code>!==</code> compares X and Z too. With <code>!=</code>, an X would make the result X and the if would just fall through.'),
        ('task automatic test_flags;', 'Test 2. 문턱의 <strong>양쪽</strong>을 본다. 05 절에서 고친 판이다. 아래 커밋 뷰어에 무엇이 바뀌었는지 있다.', 'Test 2 checks <strong>both sides</strong> of each threshold. This is the version fixed in section 05; the commit viewer below shows the change.'),
        ('err_mark = errors;', '지금까지의 에러 수를 적어둔다. 끝에 안 늘었을 때만 "correct" 를 찍는다.', 'Note the error count so far; "correct" is printed only if it has not grown.'),
        ('@(posedge wclk);', '11 개를 쓴 뒤 한 엣지 기다린다. <code>almost_full</code> 은 등록된 출력이라 한 엣지 뒤에 반영된다. 여기서는 <strong>낮아야</strong> 한다.', 'After 11 writes, wait one edge: <code>almost_full</code> is registered and shows up an edge later. Here it must be <strong>low.</strong>'),
        ('write_word(8\'h20 + AF_LEVEL - 1);', '12 번째. 문턱을 넘는 쓰기다. 다음 엣지에 <strong>서야</strong> 한다.', 'The 12th, the write that crosses. By the next edge it <strong>must</strong> be high.'),
        ('wait (!almost_empty);', '<code>almost_empty</code> 는 <strong>건너온</strong> 쓰기 포인터로 계산된다. 판정 전에 그 포인터가 도착했는지부터 기다린다. 03 절의 지연이 testbench 를 여기서 문다.', '<code>almost_empty</code> is computed from the write pointer <strong>after it crosses.</strong> Wait for it to arrive before judging. Section 03\'s delay bites the testbench right here.'),
        ('task automatic test_simultaneous;', 'Test 3. 이 task 만 들여쓰기가 한 단 덜 들어가 있다. 원래 판이 그렇고 동작과는 무관하다.', 'Test 3. This task alone sits one indent level out; that is how it arrived, and it does not affect behaviour.'),
        ('for (wi = 0; wi < 4; wi = wi + 1)', '<strong>먼저 네 개를 넣어둔다.</strong> 처음 판에는 이게 없어서 읽기가 빈 FIFO 앞에서 영영 기다렸다 (07 절).', '<strong>Preload four entries first.</strong> The first version lacked this, and the reader waited forever on an empty FIFO (section 07).'),
        ('fork', '쓰기와 읽기를 동시에 돌린다. <code>join</code> 은 둘 다 끝날 때까지 기다린다.', 'Writer and reader run concurrently; <code>join</code> waits for both.'),
        ('if ($test$plusargs("TEST_FILL_EMPTY")) begin', 'plusarg 로 테스트를 고른다. 한 번 컴파일한 <code>simv</code> 로 셋 다 돌린다.', 'The plusarg picks the test, so one compiled <code>simv</code> runs all three.'),
        ('if (tracing) begin', '추적 파일을 닫는다. 마지막 변화까지 찍히도록 50 ns 기다린 뒤.', 'Close the trace, 50 ns later so the last transitions make it in.'),
      ]),
]

P1TB_TREES = [
    (T('코드 윤곽', 'outline'), [
        N('tb_async_fifo', file='tb', kids=[
            N(T('문턱 · 신호 · DUT', 'thresholds · signals · DUT'), file='tb', at='localparam int AF_LEVEL'),
            N(T('두 clock', 'two clocks'), file='tb', at='forever #5 wclk'),
            N(T('추적 (+TRACE)', 'trace (+TRACE)'), file='tb', at='int    trace_fd;'),
            N('reset_fifo', file='tb', at='task automatic reset_fifo;'),
            N('write_word', file='tb', at='task automatic write_word('),
            N('read_word', file='tb', at='task automatic read_word('),
            N('Test 1 · test_fill_empty', file='tb', at='task automatic test_fill_empty;'),
            N('Test 2 · test_flags', file='tb', at='task automatic test_flags;'),
            N('Test 3 · test_simultaneous', file='tb', at='task automatic test_simultaneous;'),
            N(T('plusarg 로 고르기', 'plusarg dispatch'), file='tb', at='if ($test$plusargs("TEST_FILL_EMPTY"))')])]),
]
