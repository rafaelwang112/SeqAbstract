module tb_shf;
    logic       clk;
    logic       rst_n;
    logic [2:0] amt;
    logic [7:0] q;

    shf_unit dut (
        .clk(clk),
        .rst_n(rst_n),
        .amt(amt),
        .q(q)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    integer cyc;
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_shf);
        rst_n = 1'b0;
        amt   = 3'd0;
        repeat (4) @(posedge clk);
        rst_n = 1'b1;

        for (cyc = 0; cyc < 256; cyc = cyc + 1) begin
            @(posedge clk);
            if ((cyc % 16) == 0)
                amt = 3'd1;
            else
                amt = 3'd0;
        end

        @(posedge clk);
        $finish;
    end
endmodule
