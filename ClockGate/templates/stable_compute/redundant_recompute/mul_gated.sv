module mul_unit (
    input  logic       clk,
    input  logic       rst_n,
    input  logic [3:0] a,
    input  logic [3:0] b,
    output logic [7:0] p
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            p <= 8'd0;
        else if (({4'd0, a} * {4'd0, b}) != p)
            p <= {4'd0, a} * {4'd0, b};
    end
endmodule
