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
