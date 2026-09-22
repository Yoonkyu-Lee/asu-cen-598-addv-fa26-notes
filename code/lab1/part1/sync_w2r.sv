module sync_w2r #(
    parameter int ADDR_WIDTH = 4
)(
    output logic [ADDR_WIDTH:0] rq2_wptr,
    input  logic [ADDR_WIDTH:0] wptr,
    input  logic                  rclk,
    input  logic                  rrst_n
);

    logic [ADDR_WIDTH:0] rq1_wptr;

    always_ff @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) begin
            rq1_wptr <= '0;
            rq2_wptr <= '0;
        end
        else begin
            rq1_wptr <= wptr;
            rq2_wptr <= rq1_wptr;
        end
    end

endmodule
