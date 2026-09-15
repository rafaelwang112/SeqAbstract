// Reference rewrite: same behavior, clock enable now visible in the code shape.
// Synthesis CAN gate this. That is the point of the rewrite.
module acc_unit (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [7:0]  delta,
    output logic [15:0] acc
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            acc <= 16'd0;
        else if (delta != 8'd0)
            acc <= acc + {8'd0, delta};
    end
endmodule
