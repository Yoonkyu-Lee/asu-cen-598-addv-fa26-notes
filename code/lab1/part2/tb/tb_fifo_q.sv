// fifo_q 레벨 testbench. 동기 구현과 비동기 구현이 이것 하나를 공유한다.
//
// 목적이 둘이다.
//   1. 갈아끼울 두 구현이 같은 계약을 정말로 지키는지 확인한다
//   2. 두 구현을 가르는 숫자 하나를 잰다. 빈 FIFO 에 데이터가 들어온 뒤
//      empty 가 풀릴 때까지 몇 사이클이 걸리는가
//
// 2번이 이 파일의 존재 이유다. 비동기 FIFO 를 클럭 하나로 묶어 쓰면 안쪽의
// 2단 동기화기 때문에 empty 가 늦게 풀린다. 그게 몇 사이클인지 추측하지 않고
// 여기서 센다.
//
// 계약에서 rd_data 의 의미는 "지금 머리에 있는 값" 이다. rd_en 은 그것을 꺼낸다.
// 그래서 읽을 때는 rd_data 를 먼저 보고 rd_en 을 올린다.

// 깊이는 Makefile 이 넘긴다. 동기는 40, 비동기는 64 다. 상위 회로가 실제로
// 쓰는 깊이 그대로 FIFO 를 검증해야 의미가 있다.
`ifndef FIFO_DEPTH
  `define FIFO_DEPTH 64
`endif

module tb_fifo_q;

    localparam int DATA_WIDTH = 8;
    localparam int DEPTH      = `FIFO_DEPTH;

    logic                  clk;
    logic                  rst_n;

    logic                  wr_en;
    logic [DATA_WIDTH-1:0] wr_data;

    logic                  rd_en;
    logic [DATA_WIDTH-1:0] rd_data;

    logic                  full;
    logic                  empty;

    integer errors;
    integer empty_latency;


    fifo_q #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (DEPTH)
    ) dut (
        .*
    );


    // 클럭 하나. Part 2 는 단일 클럭 회로다.
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    initial begin
        $fsdbDumpfile("novas.fsdb");
        $fsdbDumpvars(0, tb_fifo_q);
    end


    task automatic reset_fifo;
        begin
            wr_en   = 1'b0;
            rd_en   = 1'b0;
            wr_data = '0;
            rst_n   = 1'b0;
            repeat (4) @(posedge clk);
            @(negedge clk);
            rst_n = 1'b1;
            repeat (4) @(posedge clk);
        end
    endtask


    task automatic push(input logic [DATA_WIDTH-1:0] d);
        begin
            @(negedge clk);
            wr_data = d;
            wr_en   = 1'b1;
            @(negedge clk);
            wr_en   = 1'b0;
        end
    endtask


    task automatic pop(output logic [DATA_WIDTH-1:0] d);
        begin
            @(negedge clk);
            d     = rd_data;      // 머리에 있는 값을 먼저 본다
            rd_en = 1'b1;         // 그리고 꺼낸다
            @(negedge clk);
            rd_en = 1'b0;
        end
    endtask


    //--------------------------------------------------------------------
    // A. empty 가 풀리는 데 걸리는 사이클.
    //    두 구현을 가르는 숫자다. 빈 FIFO 에 한 개 넣고, empty 가 0 이
    //    될 때까지 posedge 를 센다.
    //--------------------------------------------------------------------
    task automatic measure_empty_latency;
        integer n;
        begin
            reset_fifo();

            if (!empty) begin
                $error("FIFO should be empty after reset.");
                errors = errors + 1;
            end

            push(8'hA5);

            // 쓰기가 실린 엣지 뒤로 몇 엣지가 지나야 empty 가 내려가나를 센다.
            //
            // 엣지마다 1ns 기다린 뒤에 본다. @(posedge clk) 직후에 바로 읽으면 그
            // 순간에는 설계의 always_ff 가 아직 값을 안 바꿨다 (NBA 영역이 뒤에 온다).
            // 그러면 empty 가 내려가는 바로 그 엣지에서 옛 값 1 을 읽어서 한 번 더 센다.
            //
            // 처음에는 그렇게 읽어서 비동기 판이 4 로 나왔다. 상위 회로 트레이스에서
            // 첫 출력이 동기 cycle 2, 비동기 cycle 5 로 차이가 3 이라 어긋났고, 그걸로
            // 찾았다. 동기 판은 empty 가 쓰기 엣지에서 이미 내려가 이 루프를 안 타므로
            // 영향이 없었다.
            n = 0;
            while (empty && n < 20) begin
                @(posedge clk);
                #1;
                n = n + 1;
            end

            empty_latency = n;

            if (empty) begin
                $error("empty never cleared after a write.");
                errors = errors + 1;
            end
            else begin
                $display("RESULT empty_latency = %0d cycle(s)", n);
            end

            if (rd_data !== 8'hA5) begin
                $error("head should be A5, got %02h", rd_data);
                errors = errors + 1;
            end
        end
    endtask


    //--------------------------------------------------------------------
    // B. 가득 채우고 다 빼기. 순서와 값까지 본다.
    //--------------------------------------------------------------------
    task automatic fill_and_drain;
        logic [DATA_WIDTH-1:0] got;
        integer i;
        begin
            reset_fifo();

            for (i = 0; i < DEPTH; i = i + 1)
                push(i[DATA_WIDTH-1:0]);

            repeat (4) @(posedge clk);

            if (!full) begin
                $error("full should be asserted after %0d writes.", DEPTH);
                errors = errors + 1;
            end

            for (i = 0; i < DEPTH; i = i + 1) begin
                pop(got);
                if (got !== i[DATA_WIDTH-1:0]) begin
                    $error("order broken at %0d: expected %02h, got %02h",
                           i, i[DATA_WIDTH-1:0], got);
                    errors = errors + 1;
                end
            end

            repeat (4) @(posedge clk);

            if (!empty) begin
                $error("empty should be asserted after draining.");
                errors = errors + 1;
            end

            $display("RESULT fill_and_drain: %0d entries in order", DEPTH);
        end
    endtask


    //--------------------------------------------------------------------
    // C. 쓰면서 동시에 읽기. 상위 회로가 실제로 쓰는 모양이다.
    //--------------------------------------------------------------------
    task automatic stream;
        logic [DATA_WIDTH-1:0] got;
        integer i;
        begin
            reset_fifo();

            for (i = 0; i < 8; i = i + 1)
                push(8'h40 + i[DATA_WIDTH-1:0]);

            repeat (4) @(posedge clk);

            for (i = 8; i < 32; i = i + 1) begin
                @(negedge clk);
                wr_data = 8'h40 + i[DATA_WIDTH-1:0];
                wr_en   = 1'b1;
                got     = rd_data;
                rd_en   = 1'b1;
                @(negedge clk);
                wr_en   = 1'b0;
                rd_en   = 1'b0;

                if (got !== 8'h40 + (i - 8)) begin
                    $error("stream mismatch at %0d: expected %02h, got %02h",
                           i - 8, 8'h40 + (i - 8), got);
                    errors = errors + 1;
                end
            end

            $display("RESULT stream: 24 simultaneous read/write pairs in order");
        end
    endtask


    initial begin
        errors        = 0;
        empty_latency = -1;

        $display("=================================");
        $display("fifo_q level testbench");
        $display("=================================");

        measure_empty_latency();
        fill_and_drain();
        stream();

        if (errors == 0)
            $display("TEST PASSED. empty_latency=%0d", empty_latency);
        else
            $display("TEST FAILED with %0d error(s). empty_latency=%0d",
                     errors, empty_latency);

        #50;
        $finish;
    end

endmodule
