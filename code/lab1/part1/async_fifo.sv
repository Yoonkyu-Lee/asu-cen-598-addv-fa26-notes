module async_fifo #(
    parameter int DATA_WIDTH = 8,
    parameter int DEPTH      = 16
)(
    output logic [DATA_WIDTH-1:0] rdata,
    output logic                  wfull,
    output logic                  rempty,
    output logic                  almost_full,
    output logic                  almost_empty,

    input  logic [DATA_WIDTH-1:0] wdata,
    input  logic                  winc,
    input  logic                  wclk,
    input  logic                  wrst_n,

    input  logic                  rinc,
    input  logic                  rclk,
    input  logic                  rrst_n
);

    localparam int ADDR_WIDTH = $clog2(DEPTH);

    logic [ADDR_WIDTH-1:0] waddr;
    logic [ADDR_WIDTH-1:0] raddr;

    logic [ADDR_WIDTH:0] wptr;
    logic [ADDR_WIDTH:0] rptr;

    logic [ADDR_WIDTH:0] wq2_rptr;
    logic [ADDR_WIDTH:0] rq2_wptr;


    fifo_if #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) mem_if();


    assign mem_if.wdata  = wdata;
    assign mem_if.waddr  = waddr;
    assign mem_if.raddr  = raddr;
    assign mem_if.wclk   = wclk;
    assign mem_if.wclken = winc;
    assign mem_if.wfull  = wfull;

    assign rdata = mem_if.rdata;


    sync_r2w #(
        .ADDR_WIDTH(ADDR_WIDTH)
    ) sync_r2w (
        .*
    );


    sync_w2r #(
        .ADDR_WIDTH(ADDR_WIDTH)
    ) sync_w2r (
        .*
    );


    fifo_mem #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) fifo_mem (
        .*
    );


    fifo_rptr #(
        .ADDR_WIDTH(ADDR_WIDTH)
    ) fifo_rptr (
        .*
    );


    fifo_wptr #(
        .ADDR_WIDTH(ADDR_WIDTH)
    ) fifo_wptr (
        .*
    );

endmodule
