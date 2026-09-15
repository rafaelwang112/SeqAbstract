module tb_mul;
    logic       clk;
    logic       rst_n;
    logic [3:0] a;
    logic [3:0] b;
    logic [7:0] p;
    logic       chg;

    mul_unit dut (
        .clk(clk),
        .rst_n(rst_n),
        .a(a),
        .b(b),
        .p(p)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    integer cyc;
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_mul);
        rst_n = 1'b0;
        a     = 4'd1;
        b     = 4'd3;
        chg   = 1'b0;
        repeat (4) @(posedge clk);
        rst_n = 1'b1;

        for (cyc = 0; cyc < 256; cyc = cyc + 1) begin
            @(posedge clk);
            if ((cyc % 16) == 0) begin
                a   = a + 4'd1;
                b   = b + 4'd2;
                chg = 1'b1;
            end else
                chg = 1'b0;
        end

        @(posedge clk);
        $finish;
    end
endmodule
