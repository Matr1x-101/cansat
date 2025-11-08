import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import NMF

# create Synthetic Data Representing the 4 Source Types
np.random.seed(42)
n_samples = 200
time = np.linspace(0, 10, n_samples)

# define pollutant species
columns = ['CO', 'NO2', 'NH3', 'PM25']

# source fingerprints (relative emissions)
true_profiles = np.array([
    [8, 9, 1, 2],   # Mobile sources, high CO & NO2
    [4, 6, 2, 5],   # Industrial stationary, CO, NO2, PM25 moderate
    [1, 1, 10, 2],  # Agricultural / area sources, very high NH3
    [1, 2, 1, 12]   # Natural (dust, wildfire), high PM2.5
])

# time-varying contributions (just synthetic patterns)
factor_contrib = np.vstack([
    2 + np.sin(time*1.2),      # mobile varies frequently (traffic)
    1.5 + 0.5*np.cos(time/2),  # industrial stable
    1 + np.sin(time/3),        # agricultural seasonal-type change
    0.8 + 0.3*np.sin(time*0.5) # natural background
]).T

# create observed data
X = factor_contrib @ true_profiles + np.random.normal(scale=0.4, size=(n_samples, 4))
df = pd.DataFrame(X, columns=columns)

# aply NMF to recover factors ---
model = NMF(n_components=4, init="nndsvda", max_iter=2000, random_state=0)
W = model.fit_transform(df.values)
H = model.components_

# normalise profiles to interpret as fingerprints
profiles = pd.DataFrame(H, columns=columns, index=["Mobile", "Stationary", "Area", "Natural"])
profiles = profiles.div(profiles.sum(axis=1), axis=0)

# percent contributions over time
contrib_pct = pd.DataFrame(W, columns=profiles.index)
contrib_pct = contrib_pct.div(contrib_pct.sum(axis=1), axis=0) * 100

# visualisations
# pollutant time series
plt.figure()
df.plot(figsize=(8,4))
plt.title("Synthetic Pollutant Time Series")
plt.xlabel("Sample Index")
plt.ylabel("Concentration (a.u.)")
plt.savefig("pollutant_time_series.png", dpi=300, bbox_inches='tight')
plt.close()

# fingerprint profiles
plt.figure()
profiles.plot(kind="bar", figsize=(8,4))
plt.title("Recovered Source Fingerprints (NMF Factors)")
plt.ylabel("Relative Species Contribution")
plt.savefig("source_fingerprints.png", dpi=300, bbox_inches='tight')
plt.close()

# time-varying contributions
plt.figure()
contrib_pct.plot(figsize=(8,4))
plt.title("Time-Varying Source Contributions (%)")
plt.ylabel("Percent Contribution")
plt.savefig("source_contributions.png", dpi=300, bbox_inches='tight')
plt.close()
