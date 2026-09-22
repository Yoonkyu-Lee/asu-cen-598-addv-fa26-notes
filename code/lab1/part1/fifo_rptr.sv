module fifo_rptr #(
    parameter int ADDR_WIDTH = 4
)(
    output logic                  rempty,
    output logic                  almost_empty,
    output logic [ADDR_WIDTH-1:0] raddr,
    output logic [ADDR_WIDTH:0]   rptr,

    input  logic [ADDR_WIDTH:0]   rq2_wptr,
    input  logic                  rinc,
    input  logic                  rclk,
    input  logic                  rrst_n
);

    localparam int DEPTH = 1 << ADDR_WIDTH;
    localparam int ALMOST_EMPTY_LEVEL = DEPTH / 4;

    logic [ADDR_WIDTH:0] rbin;
    logic [ADDR_WIDTH:0] rbinnext;
    logic [ADDR_WIDTH:0] rgraynext;

    logic [ADDR_WIDTH:0] rq2_wbin;
    logic [ADDR_WIDTH:0] rused_next;

    logic rempty_val;
    logic almost_empty_val;


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

        rbinnext = rbin + (rinc && !rempty);

        rgraynext = (rbinnext >> 1) ^ rbinnext;

        rq2_wbin = gray2bin(rq2_wptr);

        rused_next = rq2_wbin - rbinnext;

        rempty_val = (rgraynext == rq2_wptr);

        almost_empty_val =
            (rused_next <= ALMOST_EMPTY_LEVEL);

    end


    always_ff @(posedge rclk or negedge rrst_n) begin

        if (!rrst_n) begin

            rbin         <= '0;
            rptr         <= '0;
            rempty       <= 1'b1;
            almost_empty <= 1'b1;

        end
        else begin

            rbin         <= rbinnext;
            rptr         <= rgraynext;
            rempty       <= rempty_val;
            almost_empty <= almost_empty_val;

        end

    end


    assign raddr = rbin[ADDR_WIDTH-1:0];

endmodule
