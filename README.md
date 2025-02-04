# PolyAnalyst

PolyAnalyst is a program that analyses solutions of polynomials in integers.

## About
Given a polynomial in k variables, PolyAnalyst finds:
- Number of integer solutions for each n in a given range [a,b]
- Visual representation of the polynomial

## Available Versions
- **PolyAnalyst.exe**: Analyzes solutions in all integers (both positive and negative)
- **PolyAnalystN.exe**: Analyzes solutions only in natural numbers (non-negative integers)

## How to Use
1. Enter your polynomial (Example: x**2 + y**2)
2. Enter variables separated by commas (Example: x, y)
3. Set the range [a,b] for n
4. Set the search range for variables
5. Click "Analyze"

## Example
For the polynomial x**2 + y**2 = n:
- The program finds how many ways each number n can be written as a sum of two squares
- Shows all solutions for each n in the given range
- Provides an upper bound for the growth rate of solutions

## Notes
- For large ranges, computation time may increase
- Visualization is available for polynomials with 1 or 2 variables
