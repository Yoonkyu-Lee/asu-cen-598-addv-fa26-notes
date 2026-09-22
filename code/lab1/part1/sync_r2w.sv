module sync_r2w #(
    parameter int ADDR_WIDTH = 4
)(
    output logic [ADDR_WIDTH:0] wq2_rptr,
    input  logic [ADDR_WIDTH:0] rptr,
    input  logic                  wclk,
    input  logic                  wrst_n
);

    logic [ADDR_WIDTH:0] wq1_rptr;

    always_ff @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) begin
            wq1_rptr <= '0;
            wq2_rptr <= '0;
        end
        else begin
            wq1_rptr <= rptr;
            wq2_rptr <= wq1_rptr;
        end
    end

endmodule
