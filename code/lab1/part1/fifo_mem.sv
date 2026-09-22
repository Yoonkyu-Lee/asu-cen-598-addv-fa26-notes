module fifo_mem #(
    parameter int DATA_WIDTH = 8,
    parameter int ADDR_WIDTH = 4
)(
    fifo_if.mem mem_if
);

    localparam int DEPTH = 1 << ADDR_WIDTH;

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    assign mem_if.rdata = mem[mem_if.raddr];

    always_ff @(posedge mem_if.wclk) begin
        if (mem_if.wclken && !mem_if.wfull)
            mem[mem_if.waddr] <= mem_if.wdata;
    end

endmodule
