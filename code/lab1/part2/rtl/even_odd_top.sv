// Even/Odd Alternating Circuit. Lab 1 Part II 의 최상위 모듈이다.
//
// 짝수와 홀수가 아무 순서로나 섞여 들어오는 스트림을 받아, 짝과 홀이 반드시
// 번갈아 나오는 스트림으로 내보낸다. 같은 parity 안에서의 순서는 입력 순서를
// 그대로 지킨다.
//
//   입력:  3  7  4  9  6  2  5  8
//   출력:  3  4  7  6  9  2  5  8
//          홀 짝 홀 짝 홀 짝 홀 짝
//
// 구조는 Lab 의 힌트 그대로다. FIFO 두 개 (짝수용, 홀수용) 를 두고 그 주위에
// 얇은 로직을 감는다.
//
//   쓰기 쪽: 조합 로직뿐이다. Data_in[0] 하나로 어느 FIFO 에 넣을지 갈린다
//   읽기 쪽: 2상태 FSM. 지금 내보낼 차례가 짝인지 홀인지만 기억한다
//
// FIFO 구현은 갈아끼운다. 여기서는 fifo_q 라는 이름으로만 부르고, 그게
// rtl/sync/fifo_q.sv 인지 rtl/async/fifo_q.sv 인지는 Makefile 의 VARIANT 가
// 정한다. 이 파일은 두 경우에 한 글자도 안 바뀐다.
//
// -------------------------------------------------------------------------
// 포트 이름은 Lab 의 인터페이스 표를 그대로 따른다. Reset 은 active high 다.
// 안쪽 FIFO 는 active low (rst_n) 를 쓰므로 여기서 한 번 뒤집어 넘긴다.
// -------------------------------------------------------------------------

module even_odd_top #(
    parameter int DATA_WIDTH = 8,

    // 두 FIFO 의 깊이. 40 이면 충분하다. 근거는 MEASUREMENTS.md 에 있다.
    // 비동기 구현은 gray code 때문에 2의 거듭제곱이어야 하므로 64 로 올려야 한다.
    // 동기 구현은 40 을 그대로 쓸 수 있다. 그 차이가 두 구현을 비교하는 한 축이다.
    parameter int FIFO_DEPTH = 64
)(
    input  logic                  Clock,
    input  logic                  Reset,

    input  logic [DATA_WIDTH-1:0] Data_in,
    input  logic                  Write_en,

    output logic [DATA_WIDTH-1:0] Data_out,
    input  logic                  Read_en
);

    // 안쪽 FIFO 들이 쓰는 active low reset.
    logic rst_n;
    assign rst_n = ~Reset;


    //======================================================================
    // 쓰기 쪽. 조합 로직뿐이다.
    //
    // 최하위 비트 하나가 parity 다. Data_in[0] 이 0 이면 짝수, 1 이면 홀수.
    // 나눗셈도 비교기도 필요 없다. 배선 한 가닥이다.
    //======================================================================

    logic even_wr_en;
    logic odd_wr_en;

    always_comb begin
        even_wr_en = Write_en && (Data_in[0] == 1'b0);
        odd_wr_en  = Write_en && (Data_in[0] == 1'b1);
    end

    // full 은 보지 않는다. Lab 이 "You will not need to use the fifo_full ...
    // flags" 라고 적었고, FIFO 가 스스로 가득 찼을 때의 쓰기를 무시하기 때문이다.
    // 깊이가 정말 충분한지는 testbench 가 dut 안쪽 full 을 직접 들여다보며 감시한다.


    //======================================================================
    // FIFO 두 개
    //======================================================================

    logic [DATA_WIDTH-1:0] even_rd_data;
    logic [DATA_WIDTH-1:0] odd_rd_data;
    logic                  even_empty;
    logic                  odd_empty;
    logic                  even_full;
    logic                  odd_full;
    logic                  even_rd_en;
    logic                  odd_rd_en;

    fifo_q #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (FIFO_DEPTH)
    ) u_fifo_even (
        .clk     (Clock),
        .rst_n   (rst_n),
        .wr_en   (even_wr_en),
        .wr_data (Data_in),
        .rd_en   (even_rd_en),
        .rd_data (even_rd_data),
        .full    (even_full),
        .empty   (even_empty)
    );

    fifo_q #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (FIFO_DEPTH)
    ) u_fifo_odd (
        .clk     (Clock),
        .rst_n   (rst_n),
        .wr_en   (odd_wr_en),
        .wr_data (Data_in),
        .rd_en   (odd_rd_en),
        .rd_data (odd_rd_data),
        .full    (odd_full),
        .empty   (odd_empty)
    );


    //======================================================================
    // 읽기 쪽. 2상태 FSM.
    //
    // 상태는 "다음에 내보낼 차례" 하나뿐이다. SEL_EVEN 이면 짝수 FIFO 에서,
    // SEL_ODD 면 홀수 FIFO 에서 꺼낸다. 한 번 꺼낼 때마다 뒤집는다. 그래서
    // 출력에 같은 parity 가 연속으로 나올 수 없다. 구조가 그것을 보장한다.
    //
    // 차례인 FIFO 가 비어 있으면 **멈춘다.** Read_en 이 올라와 있어도 꺼내지
    // 않고, 상태도 안 뒤집고, Data_out 도 안 바꾼다. Lab 의 요구다.
    //
    //   "The circuit has to pause or stay in idle state if one of the FIFOs
    //    is empty and should not output a 0."
    //
    // 반대편 FIFO 에 데이터가 쌓여 있어도 꺼내지 않는다. 꺼내면 같은 parity 가
    // 두 번 연속 나가기 때문이다. 멈추는 것이 맞다.
    //======================================================================

    typedef enum logic {
        SEL_EVEN = 1'b0,
        SEL_ODD  = 1'b1
    } sel_e;

    sel_e sel;

    // 첫 출력의 parity 를 첫 입력의 parity 에 맞춘다.
    //
    // 이게 없으면 FSM 이 항상 짝수부터 내보내려 한다. 입력이 홀수로 시작하면
    // 첫 짝수가 들어올 때까지 아무것도 못 내보내고 헛돈다. 기능은 맞지만
    // 느리고, 위의 예시 (3 으로 시작하는 입력) 와도 어긋난다.
    //
    // 그래서 reset 이후 처음 들어온 데이터의 parity 로 시작 상태를 정한다.
    // started 가 그 "아직 한 개도 안 들어왔다" 를 기억하는 비트다.
    logic started;

    logic                  sel_empty;
    logic [DATA_WIDTH-1:0] sel_data;

    always_comb begin
        sel_empty = (sel == SEL_EVEN) ? even_empty   : odd_empty;
        sel_data  = (sel == SEL_EVEN) ? even_rd_data : odd_rd_data;
    end

    // 실제로 꺼내지는 순간. 소비자가 요청했고, 차례인 FIFO 에 물건이 있을 때만이다.
    logic do_pop;
    assign do_pop = Read_en && !sel_empty;

    always_comb begin
        even_rd_en = do_pop && (sel == SEL_EVEN);
        odd_rd_en  = do_pop && (sel == SEL_ODD);
    end

    // Data_out 은 등록된 출력이다. 꺼낸 값만 실리고, 멈춰 있는 동안에는
    // 직전 값을 그대로 붙들고 있는다. 그래서 "0 을 내보내지 않는다" 가
    // 저절로 지켜진다. 비어 있는 FIFO 의 rd_data 는 쳐다보지도 않는다.
    //
    // out_valid 는 설계의 포트가 아니다. Lab 의 인터페이스 표에 없는 신호를
    // 밖으로 빼지 않기 위해 안에만 둔다. testbench 가 계층 참조로 들여다보며
    // "이번 사이클에 진짜 나온 값인가" 를 판정한다.
    logic out_valid;

    always_ff @(posedge Clock) begin

        if (Reset) begin
            sel       <= SEL_EVEN;
            started   <= 1'b0;
            Data_out  <= '0;
            out_valid <= 1'b0;
        end
        else begin

            out_valid <= do_pop;

            if (do_pop) begin
                Data_out <= sel_data;
                sel      <= (sel == SEL_EVEN) ? SEL_ODD : SEL_EVEN;
            end

            // 첫 입력이 시작 parity 를 정한다. 딱 한 번만 먹는다.
            // 같은 사이클에 do_pop 이 설 수는 없다. started 가 0 이라는 것은
            // 두 FIFO 가 다 비어 있다는 뜻이고, 그러면 sel_empty 가 1 이다.
            if (Write_en && !started) begin
                started <= 1'b1;
                sel     <= Data_in[0] ? SEL_ODD : SEL_EVEN;
            end

        end

    end

endmodule
