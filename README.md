# droplet_stationalSurface_impact

list setFieldsDict dambreak

This is all what you need to simulate droplet imapact via OpenFOAM.

Usage: Use the following commands in order.

>blockMesh

>setFields

>interFoam

>paraFoam
I'll create a comprehensive markdown document explaining the OpenFOAM setup for the gasoline droplet impact simulation.

# OpenFOAM Gasoline Droplet Impact Simulation Setup Guide

## Directory Structure
```
gasoline/
├── 0/                  # Initial conditions directory
├── constant/           # Physical properties and mesh
├── system/             # Simulation control parameters
└── gasolineDrop.foam   # Empty file for ParaView visualization
```

## Initial Conditions (0/)

### `alpha.gasoline`
This file defines the volume fraction field for gasoline.

```cpp
dimensions      [0 0 0 0 0 0 0];  // Dimensionless field
internalField   uniform 0;        // Initially set to 0 everywhere
```

Boundary conditions:
- `lowerWall`, `leftWall`, `rightWall`: `zeroGradient` - no flux through walls
- `atmosphere`: `inletOutlet` - allows fluid to enter/exit
- `frontAndBack`: `empty` - 2D simulation

### `p_rgh`
Defines the dynamic pressure field (pressure minus hydrostatic pressure).

```cpp
dimensions      [1 -1 -2 0 0 0 0];  // kg/(m·s²)
internalField   uniform 0;          // Initially zero pressure
```

Boundary conditions:
- `lowerWall`, `leftWall`, `rightWall`: `fixedFluxPressure` - maintains zero flux at walls
- `atmosphere`: `totalPressure` with `p0 uniform 0` - atmospheric condition
- `frontAndBack`: `empty` - 2D simulation

### `U`
Defines the velocity field.

```cpp
dimensions      [0 1 -1 0 0 0 0];    // m/s
internalField   uniform (0 0 0);     // Initially zero velocity
```

Boundary conditions:
- `lowerWall`, `leftWall`: `noSlip` - zero velocity at walls
- `rightWall`, `atmosphere`: `pressureInletOutletVelocity` - allows flow based on pressure
- `frontAndBack`: `empty` - 2D simulation

## Mesh Configuration (system/blockMeshDict)

```cpp
vertices
(
    (0 0 0)       // Point 0
    (75 0 0)      // Point 1
    (75 6 0)      // Point 2
    (0 6 0)       // Point 3
    (0 0 0.1)     // Point 4
    (75 0 0.1)    // Point 5
    (75 6 0.1)    // Point 6
    (0 6 0.1)     // Point 7
);
```

Mesh parameters:
- Domain size: 75×6×0.1 units
- Cell count: `(1000 80 1)` - refined in impact region
- Grading: 2 in x-direction for better resolution near impact

## Initial Setup (system/setFieldsDict)

Defines initial droplet and pool configuration:

```cpp
regions
(
    boxToCell
    {
        box (0 0 0) (75 3 0.1);   // Pool region
        fieldValues
        (
            volScalarField alpha.gasoline 1
        );
    }

    sphereToCell
    {
        centre (37.5 5 0.05);     // Droplet position
        radius 1.0;               // Droplet radius
        fieldValues
        (
            volScalarField alpha.gasoline 1
            volVectorField U (0 -1 0)  // Initial velocity
        );
    }
);
```

## Solution Control (system/fvSolution)

### Solver settings:
- `alpha.gasoline`: MULES algorithm with `nAlphaCorr 2`
- `p_rgh`: GAMG solver with DIC preconditioner
- `U`: smoothSolver with symGaussSeidel smoother

### PIMPLE algorithm parameters:
- `nOuterCorrectors`: 1
- `nCorrectors`: 3
- `nNonOrthogonalCorrectors`: 1

## Physical Properties (constant/transportProperties)

```cpp
phases
(
    gasoline
    {
        transportModel  Newtonian;
        nu             [0 2 -1 0 0 0 0] 3.92e-07;  // Kinematic viscosity
        rho            [1 -3 0 0 0 0 0] 680;       // Density
    }
    air
    {
        transportModel  Newtonian;
        nu             [0 2 -1 0 0 0 0] 1.48e-05;  // Kinematic viscosity
        rho            [1 -3 0 0 0 0 0] 1;         // Density
    }
);

sigma           [1 0 -2 0 0 0 0] 0.0187;  // Surface tension
```

## Time Control (system/controlDict)

```cpp
application     interFoam;
startTime       0;
endTime         0.05;          // Simulation duration
deltaT          1e-6;          // Initial time step
writeInterval   0.01;          // Output interval
adjustTimeStep  yes;
maxCo          0.5;           // Maximum Courant number
maxAlphaCo     0.5;           // Maximum alpha Courant number
```

This setup creates a 2D simulation of a gasoline droplet impacting a gasoline pool, with appropriate physical properties, mesh resolution, and numerical controls for stable and accurate results.
