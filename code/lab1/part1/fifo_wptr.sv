module fifo_wptr #(
    parameter int ADDR_WIDTH = 4
)(
    output logic                  wfull,
    output logic                  almost_full,
    output logic [ADDR_WIDTH-1:0] waddr,
    output logic [ADDR_WIDTH:0]   wptr,

    input  logic [ADDR_WIDTH:0]   wq2_rptr,
    input  logic                  winc,
    input  logic                  wclk,
    input  logic                  wrst_n
);

    localparam int DEPTH = 1 << ADDR_WIDTH;
    localparam int ALMOST_FULL_LEVEL = (3 * DEPTH) / 4;

    logic [ADDR_WIDTH:0] wbin;
    logic [ADDR_WIDTH:0] wbinnext;
    logic [ADDR_WIDTH:0] wgraynext;

    logic [ADDR_WIDTH:0] wq2_rbin;
    logic [ADDR_WIDTH:0] wused_next;

    logic wfull_val;
    logic almost_full_val;


    function automatic logic [ADDR_WIDTH:0] gray2bin(
        input logic [ADDR_WIDTH:0] gray
    );

        logic [ADDR_WIDTH:0] bin;
        integer i;

        begin
            bin[ADDR_WIDTH] = gray[ADDR_WIDTH];

            for (i = ADDR_WIDTH-1; i >= 0; i = i-1)
                bin[i] = bin[i+1] ^ gray[i];

            gray2bin = bin;
        end

    endfunction


    always_comb begin

        wbinnext = wbin + (winc && !wfull);

        wgraynext = (wbinnext >> 1) ^ wbinnext;

        wq2_rbin = gray2bin(wq2_rptr);

        wused_next = wbinnext - wq2_rbin;

        wfull_val =
            (wgraynext ==
            {~wq2_rptr[ADDR_WIDTH:ADDR_WIDTH-1],
              wq2_rptr[ADDR_WIDTH-2:0]});

        almost_full_val =
            (wused_next >= ALMOST_FULL_LEVEL);

    end


    always_ff @(posedge wclk or negedge wrst_n) begin

        if (!wrst_n) begin

            wbin        <= '0;
            wptr        <= '0;
            wfull       <= 1'b0;
            almost_full <= 1'b0;

        end
        else begin

            wbin        <= wbinnext;
            wptr        <= wgraynext;
            wfull       <= wfull_val;
            almost_full <= almost_full_val;

        end

    end


    assign waddr = wbin[ADDR_WIDTH-1:0];

endmodule
