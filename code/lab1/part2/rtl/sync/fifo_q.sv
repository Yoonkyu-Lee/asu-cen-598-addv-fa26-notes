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

    localparam int PTR_WIDTH = (DEPTH <= 1) ? 1 : $clog2(DEPTH);

    localparam int CNT_WIDTH = $clog2(DEPTH + 1);

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    logic [PTR_WIDTH-1:0]  wptr;
    logic [PTR_WIDTH-1:0]  rptr;
    logic [CNT_WIDTH-1:0]  count;

    logic do_wr;
    logic do_rd;


    always_comb begin
        do_wr = wr_en && !full;
        do_rd = rd_en && !empty;
    end


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

            unique case ({do_wr, do_rd})
                2'b10:   count <= count + 1'b1;
                2'b01:   count <= count - 1'b1;
                default: count <= count;
            endcase

        end

    end

endmodule
