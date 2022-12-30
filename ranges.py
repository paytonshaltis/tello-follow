import numpy as np

# ( [hMin, sMin, vMin], [hMax, sMax, vMax] )
RANGES = { 
  'lime': [
    (np.array([22, 83, 60]), np.array([43, 221, 167])),
    (np.array([22, 88, 51]), np.array([47, 255, 180])),
    (np.array([22, 128, 27]), np.array([91, 255, 201])),
    (np.array([22, 129, 124]), np.array([45, 255, 255])),
    (np.array([22, 88, 48]), np.array([49, 255, 159])),
    (np.array([22, 75, 46]), np.array([42, 255, 186])),
    (np.array([22, 80, 51]), np.array([87, 203, 187])),
    (np.array([22, 146, 73]), np.array([98, 223, 237])),
    (np.array([22, 114, 119]), np.array([89, 224, 233])),
  ],
  'pink': [
    (np.array([165, 104, 165]), np.array([179, 166, 255])),
    (np.array([0, 131, 229]), np.array([179, 172, 255])),
    (np.array([0, 97, 216]), np.array([8, 123, 255])),
    (np.array([0, 100, 248]), np.array([179, 171, 255])),
    (np.array([0, 60, 248]), np.array([179, 134, 255])),
  ]
}