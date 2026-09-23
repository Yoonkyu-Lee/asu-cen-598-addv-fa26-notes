module even_odd_top #(
    parameter int DATA_WIDTH = 8,

    parameter int FIFO_DEPTH = 64
)(
    input  logic                  Clock,
    input  logic                  Reset,

    input  logic [DATA_WIDTH-1:0] Data_in,
    input  logic                  Write_en,

    output logic [DATA_WIDTH-1:0] Data_out,
    input  logic                  Read_en
);

    logic rst_n;
    assign rst_n = ~Reset;


    logic even_wr_en;
    logic odd_wr_en;

    always_comb begin
        even_wr_en = Write_en && (Data_in[0] == 1'b0);
        odd_wr_en  = Write_en && (Data_in[0] == 1'b1);
    end


    logic [DATA_WIDTH-1:0] even_rd_data;
    logic [DATA_WIDTH-1:0] odd_rd_data;
    logic                  even_empty;
    logic                  odd_empty;
    logic                  even_full;
    logic                  odd_full;
    logic                  even_rd_en;
    logic                  odd_rd_en;

    fifo_q #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (FIFO_DEPTH)
    ) u_fifo_even (
        .clk     (Clock),
        .rst_n   (rst_n),
        .wr_en   (even_wr_en),
        .wr_data (Data_in),
        .rd_en   (even_rd_en),
        .rd_data (even_rd_data),
        .full    (even_full),
        .empty   (even_empty)
    );

    fifo_q #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (FIFO_DEPTH)
    ) u_fifo_odd (
        .clk     (Clock),
        .rst_n   (rst_n),
        .wr_en   (odd_wr_en),
        .wr_data (Data_in),
        .rd_en   (odd_rd_en),
        .rd_data (odd_rd_data),
        .full    (odd_full),
        .empty   (odd_empty)
    );


    typedef enum logic {
        SEL_EVEN = 1'b0,
        SEL_ODD  = 1'b1
    } sel_e;

    sel_e sel;

    logic started;

    logic                  sel_empty;
    logic [DATA_WIDTH-1:0] sel_data;

    always_comb begin
        sel_empty = (sel == SEL_EVEN) ? even_empty   : odd_empty;
        sel_data  = (sel == SEL_EVEN) ? even_rd_data : odd_rd_data;
    end

    logic do_pop;
    assign do_pop = Read_en && !sel_empty;

    always_comb begin
        even_rd_en = do_pop && (sel == SEL_EVEN);
        odd_rd_en  = do_pop && (sel == SEL_ODD);
    end

    logic out_valid;

    always_ff @(posedge Clock) begin

        if (Reset) begin
            sel       <= SEL_EVEN;
            started   <= 1'b0;
            Data_out  <= '0;
            out_valid <= 1'b0;
        end
        else begin

            out_valid <= do_pop;

            if (do_pop) begin
                Data_out <= sel_data;
                sel      <= (sel == SEL_EVEN) ? SEL_ODD : SEL_EVEN;
            end

            if (Write_en && !started) begin
                started <= 1'b1;
                sel     <= Data_in[0] ? SEL_ODD : SEL_EVEN;
            end

        end

    end

endmodule
