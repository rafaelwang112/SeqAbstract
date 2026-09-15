// Stimulus plants the idle: delta is 0 on 15 of every 16 cycles.
// DUT is whichever acc_unit was compiled in (waste or gated).
module tb_acc;
    logic        clk;
    logic        rst_n;
    logic [7:0]  delta;
    logic [15:0] acc;

    acc_unit dut (
        .clk(clk),
        .rst_n(rst_n),
        .delta(delta),
        .acc(acc)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    integer cyc;
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_acc);
        rst_n = 1'b0;
        delta = 8'd0;
        repeat (4) @(posedge clk);
        rst_n = 1'b1;

        for (cyc = 0; cyc < 256; cyc = cyc + 1) begin
            @(posedge clk);
            // nonzero only every 16th cycle after reset window
            if ((cyc % 16) == 0)
                delta = 8'd3;
            else
                delta = 8'd0;
        end

        @(posedge clk);
        $finish;
    end
endmodule
