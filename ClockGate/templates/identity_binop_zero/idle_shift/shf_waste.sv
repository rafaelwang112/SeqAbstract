module shf_unit (
    input  logic       clk,
    input  logic       rst_n,
    input  logic [2:0] amt,
    output logic [7:0] q
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            q <= 8'h01;
        else
            q <= q << amt;
    end
endmodule
