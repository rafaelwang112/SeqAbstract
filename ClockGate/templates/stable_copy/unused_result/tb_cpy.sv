module tb_cpy;
    logic       clk;
    logic       rst_n;
    logic [7:0] din;
    logic [7:0] q;
    logic       chg;

    cpy_unit dut (
        .clk(clk),
        .rst_n(rst_n),
        .din(din),
        .q(q)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    integer cyc;
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_cpy);
        rst_n = 1'b0;
        din   = 8'd1;
        chg   = 1'b0;
        repeat (4) @(posedge clk);
        rst_n = 1'b1;

        for (cyc = 0; cyc < 256; cyc = cyc + 1) begin
            @(posedge clk);
            if ((cyc % 16) == 0) begin
                din = din + 8'd5;
                chg = 1'b1;
            end else
                chg = 1'b0;
        end

        @(posedge clk);
        $finish;
    end
endmodule
