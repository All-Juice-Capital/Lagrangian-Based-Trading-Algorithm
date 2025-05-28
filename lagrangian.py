print("\n**Disclaimer:** This code is presented solely for educational purposes, illustrating a conceptual trading strategy. The methods used for identifying significant price zones and generating trading signals are highly simplified and should not be considered suitable for real-world trading. Developing a viable trading strategy requires sophisticated techniques for identifying market forces (analogous to 'charges'), rigorous backtesting across various market conditions, careful parameter optimization (e.g., 'field_threshold', 'charge_multiplier'), and a comprehensive understanding of financial market risks. " \
"We assume no responsibility or liability for any losses incurred by individuals attempting to use this illustrative code for actual trading activities. " \
"Trading in financial markets carries substantial risk, and individuals should conduct thorough independent research and seek professional financial advice before making any trading decisions.")


import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

m = 1.0  # Mass-like constant (reflects market volatility sensitivity)
k = 10.0 # Mean reversion strength constant (how strongly prices pull back to the average)

# --- Define functions based on the LaTeX document ---
def calculate_velocity(current_price, previous_price, time_elapsed=1):
    """
    Calculates the velocity of the price, representing the rate of change.
    A larger absolute velocity indicates stronger price momentum.
    """
    if time_elapsed == 0:
        return 0
    return (current_price - previous_price) / time_elapsed

def calculate_potential_energy(price, mean_price):
    """
    Calculates the potential energy, modeling the tendency for prices to revert to the mean.
    The further the price is from the mean, the higher the potential energy.
    The constant 'k' scales the strength of this mean-reverting force.
    """
    return k * (price - mean_price)**2

def calculate_kinetic_energy(velocity, mass):
    """
    Calculates the kinetic energy, representing the energy of the price movement.
    Higher velocity (stronger momentum) results in higher kinetic energy.
    The 'mass' parameter can be thought of as inertia – how resistant the price is to changes in direction.
    """
    return 0.5 * mass * velocity**2

def calculate_lagrangian(kinetic_energy, potential_energy):
    """
    Calculates the Lagrangian, which is the difference between kinetic and potential energy.
    A positive Lagrangian suggests that the momentum (kinetic energy) is dominant over the mean-reverting force (potential energy).
    A negative Lagrangian suggests that the mean-reverting force is stronger.
    """
    return kinetic_energy - potential_energy

# --- Fetch Historical Data from Yahoo Finance ---
ticker = "AAPL"  # Example: Apple Inc.
data = yf.download(ticker, period="1y")  # Download 1 year of historical data
if data.empty:
    print(f"Could not retrieve data for {ticker} from Yahoo Finance.")
    exit()

# Extract closing prices
prices = data['Close'].values.flatten()
time = data.index  # Use the DatetimeIndex for time

# Calculate a rolling mean for the mean reversion model
window = 20  # Lookback period for the moving average
mean_price = pd.Series(prices).rolling(window=window, min_periods=1).mean().values

# Calculate velocity
velocity = np.zeros_like(prices)
for i in range(1, len(prices)):
    velocity[i] = calculate_velocity(prices[i], prices[i-1])

# Calculate potential energy
potential_energy = calculate_potential_energy(prices, mean_price)

# Calculate kinetic energy
kinetic_energy = calculate_kinetic_energy(velocity, m)

# Calculate Lagrangian
lagrangian = calculate_lagrangian(kinetic_energy, potential_energy)

# --- Identify Potential Buy Signals ---
lagrangian_threshold = -500.0
velocity_threshold = 0.1  # Adjust velocity threshold for real data
buy_signals_indices = np.where((lagrangian > lagrangian_threshold) & (velocity > velocity_threshold))[0]
buy_signals_dates = time[buy_signals_indices]

# --- Output Buy Signals to Terminal ---
print("\n--- Potential Buy Signals ---")
if len(buy_signals_dates) > 0:
    for date in buy_signals_dates:
        print(f"Buy Signal on: {date.strftime('%Y-%B-%d')}")
else:
    print("No buy signals identified based on the current parameters.")

# --- Write Buy Signals to TXT File ---
filename = f"{ticker}_buy_signals.txt"
with open(filename, "w") as f:
    f.write("--- Potential Buy Signals ---\n")
    if len(buy_signals_dates) > 0:
        for date in buy_signals_dates:
            f.write(f"Buy Signal on: {date.strftime('%Y-%B-%d')}\n")
        print(f"\nBuy signals written to: {filename}")
    else:
        f.write("No buy signals identified based on the current parameters.\n")
        print(f"\nNo buy signals to write to: {filename}")

# --- Create a Pandas DataFrame for Organized Data and Easier Plotting ---
df = pd.DataFrame({
    'Time': time,
    'Price': prices,
    'Mean Price': mean_price,
    'Velocity': velocity,
    'Potential Energy': potential_energy,
    'Kinetic Energy': kinetic_energy,
    'Lagrangian': lagrangian
})

# --- Plotting the Results to Visualize the Concepts ---
plt.figure(figsize=(15, 12))
plt.subplots_adjust(hspace=0.4) # Adjust vertical spacing between subplots

# Subplot 1: Price and Mean Price with Buy Signals
plt.subplot(4, 1, 1)
plt.plot(df['Time'], df['Price'], label='Price', color='blue')
plt.plot(df['Time'], df['Mean Price'], label=f'{window}-day Moving Average', color='red', linestyle='--')
plt.scatter(df['Time'].iloc[buy_signals_indices], df['Price'].iloc[buy_signals_indices], marker='^', color='green', s=100, label='Potential Buy Signal')
plt.title(f'APPLE Price Movement and Potential Buy Signals Based on Lagrangian')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)

# Subplot 2: Velocity of Price
plt.subplot(4, 1, 2)
plt.plot(df['Time'], df['Velocity'], label='Velocity', color='orange')
plt.axhline(velocity_threshold, color='green', linestyle='--', label=f'Velocity Threshold ({velocity_threshold:.4f})')
plt.ylabel('Price Velocity')
plt.xlabel('Date')
plt.legend()
plt.grid(True)

# Subplot 3: Kinetic and Potential Energy
plt.subplot(4, 1, 3)
plt.plot(df['Time'], df['Kinetic Energy'], label='Kinetic Energy', color='purple')
plt.plot(df['Time'], df['Potential Energy'], label='Potential Energy', color='brown')
plt.ylabel('Energy')
plt.xlabel('Date')
plt.legend()
plt.grid(True)

# Subplot 4: Lagrangian
plt.subplot(4, 1, 4)
plt.plot(df['Time'], df['Lagrangian'], label='Lagrangian', color='black')
plt.axhline(lagrangian_threshold, color='green', linestyle='--', label=f'Lagrangian Threshold ({lagrangian_threshold})')
plt.ylabel('Lagrangian (KE - PE)')
plt.xlabel('Date')
plt.legend()
plt.grid(True)

plt.suptitle(f'Lagrangian-Based Trading Algorithm Concepts Applied to {ticker}', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent overlap
plt.show()

# --- Explanation of the Code and the Concepts (Adjusted for Real Data) ---

print("\n--- Explanation of the Python Code and Concepts ---")

print("\n1. Parameter Initialization:")
print(f"   - 'm' (mass-like constant): Set to {m}. This parameter influences the kinetic energy calculation.")
print(f"   - 'k' (mean reversion strength): Set to {k}. This determines the strength of the pull towards the moving average.")

print("\n2. Identifying Potential Buy Signals:")
print(f"   - The buy condition remains the same: `lagrangian > {lagrangian_threshold}` and `velocity > {velocity_threshold:.4f}`.")
print("   - Note that the `velocity_threshold` might need adjustment based on the typical price fluctuations of the chosen asset and the data frequency.")