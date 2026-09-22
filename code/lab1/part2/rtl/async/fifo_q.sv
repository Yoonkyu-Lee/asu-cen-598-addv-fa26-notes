// fifo_q, 비동기 구현.
//
// Part 1 에서 만든 async_fifo 를 Part 2 의 동기 포트 계약에 맞춰 감싼 것뿐이다.
// Part 1 의 파일은 한 줄도 고치지 않는다.
//
// 하는 일이 셋이다.
//   1. wclk 과 rclk 을 clk 하나로 묶는다
//   2. wrst_n 과 rrst_n 을 rst_n 하나로 묶는다
//   3. almost_full 과 almost_empty 를 끊는다. Part 2 는 쓰지 않는다
//
// 주의할 점이 하나 있다. 클럭을 묶어도 안쪽의 2단 동기화기는 그대로 남는다.
// 쓰기 포인터가 읽기 쪽에 도달하는 데 여전히 두 클럭이 걸리므로, 데이터가
// 들어온 뒤에도 empty 는 두 사이클 더 1 로 남아 있다. 기능은 맞고 보수적일
// 뿐이지만, 비었다 찼다를 자주 오가는 회로에서는 처리량을 깎는다.
// 그 값이 실제로 얼마인지는 tb_fifo_q.sv 가 잰다.

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

    // Part 2 는 이 둘을 쓰지 않는다. 뜨게는 두되 밖으로 내보내지 않는다.
    logic almost_full_unused;
    logic almost_empty_unused;

    async_fifo #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (DEPTH)
    ) u_async_fifo (
        .rdata        (rd_data),
        .wfull        (full),
        .rempty       (empty),
        .almost_full  (almost_full_unused),
        .almost_empty (almost_empty_unused),

        .wdata  (wr_data),
        .winc   (wr_en),
        .wclk   (clk),
        .wrst_n (rst_n),

        .rinc   (rd_en),
        .rclk   (clk),
        .rrst_n (rst_n)
    );

endmodule
