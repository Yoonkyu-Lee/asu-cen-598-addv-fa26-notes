// fifo_q, 동기 구현. Part 2 의 제출본이 쓰는 쪽이다.
//
// Part 2 는 클럭이 하나다. 쓰는 쪽과 읽는 쪽이 같은 박자로 움직이므로
// 점유량을 세는 카운터 하나면 끝난다. 비동기 판이 gray code 와 2단 동기화기로
// 풀던 문제가 여기서는 존재하지 않는다. 포인터가 바뀌는 중간에 상대가
// 들여다볼 일이 없기 때문이다.
//
// 그 결과가 셋이다.
//   1. full 과 empty 가 카운터에서 바로 나온다. 지연이 없다
//   2. DEPTH 가 2의 거듭제곱일 필요가 없다. 포인터를 명시적으로 되감기 때문이다
//   3. 코드가 훨씬 짧다
//
// 읽기 의미는 비동기 판과 같게 맞춘다. rd_data 는 "지금 머리에 있는 값" 이고
// rd_en 이 그것을 꺼낸다. 그래야 상위 모듈이 구현을 몰라도 된다.
// empty 일 때 rd_data 는 의미가 없다. 상위 모듈이 empty 를 보고 쓰지 않는다.

module fifo_q #(
    parameter int DATA_WIDTH = 8,
    parameter int DEPTH      = 64
)(
    input  logic                  clk,
    input  logic                  rst_n,

    input  logic                  wr_en,
    input  logic [DATA_WIDTH-1:0] wr_data,

    input  logic                  rd_en,
    output logic [DATA_WIDTH-1:0] rd_data,

    output logic                  full,
    output logic                  empty
);

    // 주소는 0 부터 DEPTH-1 까지. 되감기를 손으로 하므로 2의 거듭제곱이 아니어도 된다.
    localparam int PTR_WIDTH = (DEPTH <= 1) ? 1 : $clog2(DEPTH);

    // 점유량은 0 부터 DEPTH 까지라 한 칸 더 필요하다. DEPTH=64 면 0..64 이므로 7 비트.
    localparam int CNT_WIDTH = $clog2(DEPTH + 1);

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    logic [PTR_WIDTH-1:0]  wptr;
    logic [PTR_WIDTH-1:0]  rptr;
    logic [CNT_WIDTH-1:0]  count;

    logic do_wr;
    logic do_rd;


    // 가득 찼는데 쓰거나 비었는데 읽으라고 해도 무시한다.
    always_comb begin
        do_wr = wr_en && !full;
        do_rd = rd_en && !empty;
    end


    // 카운터에서 바로 나온다. 동기화기가 없으니 늦을 이유가 없다.
    assign full  = (count == CNT_WIDTH'(DEPTH));
    assign empty = (count == '0);

    assign rd_data = mem[rptr];


    always_ff @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin
            wptr  <= '0;
            rptr  <= '0;
            count <= '0;
        end
        else begin

            if (do_wr) begin
                mem[wptr] <= wr_data;
                wptr      <= (wptr == PTR_WIDTH'(DEPTH - 1)) ? '0 : wptr + 1'b1;
            end

            if (do_rd) begin
                rptr <= (rptr == PTR_WIDTH'(DEPTH - 1)) ? '0 : rptr + 1'b1;
            end

            // 같은 사이클에 읽고 쓰면 점유량은 그대로다.
            unique case ({do_wr, do_rd})
                2'b10:   count <= count + 1'b1;
                2'b01:   count <= count - 1'b1;
                default: count <= count;
            endcase

        end

    end

endmodule
