interface fifo_if #(
    parameter int DATA_WIDTH = 8,
    parameter int ADDR_WIDTH = 4
);

    logic [DATA_WIDTH-1:0] wdata;
    logic [DATA_WIDTH-1:0] rdata;

    logic [ADDR_WIDTH-1:0] waddr;
    logic [ADDR_WIDTH-1:0] raddr;

    logic                  wclk;
    logic                  wclken;
    logic                  wfull;

    modport mem (
        input  wdata,
        input  waddr,
        input  raddr,
        input  wclk,
        input  wclken,
        input  wfull,
        output rdata
    );

endinterface
