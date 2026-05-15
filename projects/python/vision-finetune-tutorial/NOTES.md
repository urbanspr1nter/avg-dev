# NOTES

# Data Pipeline 

## Pre-Processing Step

Given: GEO TIFF and GEO JSON

- Input - GEO TIFF 
  - -> Coordinates (lat/lon) 
  - -> Sliced
  - -> Tile (W x H) at the center point (lat/lon)

- Output
1. Tile image (W x H) center point is the lat/lon
2. Pixel locations for what should be parking stall lines, handicap lines, etc.

Center point means: the latitude and longitude coordinate that is the center of your tile that was sliced from the geo tiff. You can easily convert this to the pixel location.


# Lat/Lon Pixel Resolution

A pixel corresponds to some lat/lon.


# Training Data
- Tiled (W x H) picture (clean, not drawn yet)
- A list of pixels that tells us which individual pixel in that tile belongs to a parking stall line.

Challenge?
- We only have 3 pictures labeled correctly! :( How are we going to train the model to learn off of only 3 examples?!

The model has a challenge in that it can't generalize or figure things out.

### Ask a few things:
1. For each of these 3 images... do they all look similar? Visually, and having similar setups in terms of lines? 
2. How much compute do you have? 

If yes that you have visually similar pictures, and you have time to just train repeatedly, you can get it done. 


We need to train the model repeatedly 

1. Ensure the 3 images are labeled very cleanly and well. You got all the parking lines you want.
2. Pick a model [Qwen 3.5 2B](https://huggingface.co/Qwen/Qwen3.5-2B), [Qwen 3.5 4B](https://huggingface.co/Qwen/Qwen3.5-4B) - Train in about 10 GB of VRAM
3. Train for multiple epochs - This phase is when you just overfit to those 3 images.

1 epoch: Image1, Image2, Image3, 
2 epochs: Image1, Image2, Image3, [Knowledge: 1] Image1, Image2, Image3, [Knowledge: 3] ...
3 epochs: ...

For example if you train for 5 epochs (15 examples) - it will for sure know how to inference on those 3 images. Why? Because it has been trained on them repeatedly 5 times over.

Test it, why not pick a 4th image that very visually similar, and have it inference on that to get a result. Then use that as a 4th training example. 

Next round you have 4 images. Train repeatedly again.

3x5 -> 1 good image
4x5 -> 3 good images
7x5 -> 6 good images
13x5  -> 10 good images
23x5 -> 20 good images
50x5 -> generalized

3 images but you really want somethiung to make it look different so that you can trick the model to have more...

1. For each of those images, vary the contrast, the brightness -> 3 
3x3 = 9 images

1 original image
1 image brightness: 80%, contrast: 80%
1 image brighness: 75%, contrast: 50%
1 image birghtness: 50%, contrast: 70%
1 change colorscheme maybe sepia-ish

15 images 

shift -> 4px horizontally -> shift all the pixels of the parking lines by that amount too


# Inference

2 things input:

1. The tile image (W x H)
2. Prompt - Return the coordinate locations in lat/lon of recognized parking lines in this image. The center point of the lat/lon is (LT, LO).

Output:
- List of lat/lons of all the parking lines.


# Appendix

## Geo JSON Example (One form of a result)

The following Geo JSON is the representation of the drawn lines. Basically to think about it, it is an artifact of the entire workflow. The stuff we are interested in acquiring.

```json
{
  "type": "FeatureCollection",
  "name": "PARKING_STALL_LINES",
  "crs": {
    "type": "name",
    "properties": {
      "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
    }
  },
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "MultiLineString",
        "coordinates": [
          [
            [-117.6698916718302, 33.520856371000612, 0.0],
            [-117.669935712590302, 33.520881495644069, 0.0],
            [-117.669935730759832, 33.520881521093713, 0.0],
            [-117.669935747868379, 33.520881547054181, 0.0],
            [-117.66993576389558, 33.520881573494414, 0.0],
            [-117.669935778822165, 33.520881600382843, 0.0],
            [-117.669935792630383, 33.520881627687309, 0.0],
            [-117.669935805303723, 33.52088165537522, 0.0],
            [-117.669935816826992, 33.520881683413485, 0.0],
            [-117.669935827186535, 33.520881711768595, 0.0],
            [-117.669935836369859, 33.520881740406672, 0.0],
            [-117.669935844366037, 33.520881769293474, 0.0],
            [-117.669935851165548, 33.520881798394541, 0.0],
            [-117.669935856760191, 33.520881827675048, 0.0],
            [-117.669935861143315, 33.520881857100051, 0.0],
            [-117.669935864309721, 33.520881886634335, 0.0],
            [-117.669935866255557, 33.520881916242651, 0.0],
            [-117.669935866978562, 33.520881945889599, 0.0],
            [-117.669935866477829, 33.52088197553978, 0.0],
            [-117.669935864753995, 33.520882005157794, 0.0],
            [-117.669935861809066, 33.520882034708158, 0.0],
            [-117.669935857646635, 33.520882064155643, 0.0],
            [-117.669935852271578, 33.520882093465019, 0.0],
            [-117.669935845690418, 33.520882122601293, 0.0],
            [-117.669935837910941, 33.520882151529641, 0.0],
            [-117.669935828942528, 33.520882180215509, 0.0],
            [-117.669935818795764, 33.520882208624599, 0.0],
            [-117.669935807482887, 33.520882236722976, 0.0],
            [-117.669935795017395, 33.520882264477059, 0.0],
            [-117.669935781414139, 33.520882291853688, 0.0],
            [-117.669935766689392, 33.520882318820178, 0.0],
            [-117.669935750860745, 33.520882345344269, 0.0],
            [-117.669935733947142, 33.520882371394293, 0.0],
            [-117.669935715968776, 33.520882396939122, 0.0],
            [-117.669935696947107, 33.520882421948208, 0.0],
            [-117.669935676904927, 33.52088244639171, 0.0],
            [-117.669935655866112, 33.520882470240373, 0.0],
            [-117.669935633855772, 33.520882493465749, 0.0],
            [-117.669935610900339, 33.520882516040054, 0.0],
            [-117.669935587027155, 33.520882537936316, 0.0],
            [-117.66993556226474, 33.520882559128395, 0.0],
            [-117.669935536642669, 33.520882579590946, 0.0],
            [-117.669935510191578, 33.52088259929954, 0.0],
            [-117.669935482943146, 33.520882618230587, 0.0],
            [-117.669935454929814, 33.520882636361499, 0.0],
            [-117.66993542618512, 33.520882653670647, 0.0],
            [-117.669935396743398, 33.52088267013729, 0.0],
            [-117.66993536663982, 33.520882685741761, 0.0],
            [-117.669935335910353, 33.520882700465428, 0.0],
            [-117.669935304591746, 33.520882714290714, 0.0],
            [-117.669935272721332, 33.520882727201041, 0.0],
            [-117.66993524033731, 33.520882739181062, 0.0],
            [-117.669935207478289, 33.520882750216408, 0.0],
            [-117.669935174183607, 33.520882760293915, 0.0],
            [-117.669935140492967, 33.520882769401538, 0.0],
            [-117.669935106446673, 33.520882777528392, 0.0],
            [-117.669935072085366, 33.520882784664764, 0.0],
            [-117.669935037450173, 33.520882790802091, 0.0],
            [-117.66993500258242, 33.520882795933126, 0.0],
            [-117.669934967523758, 33.520882800051695, 0.0],
            [-117.669934932316167, 33.520882803152858, 0.0],
            [-117.66993489700161, 33.520882805232908, 0.0],
            [-117.669934861622323, 33.520882806289393, 0.0],
            [-117.669934826220626, 33.520882806321019, 0.0],
            [-117.66989067823765, 33.520857701168985, 0.0],
            [-117.669890008835836, 33.520858597328207, 0.0],
            [-117.669919017003437, 33.520875225873773, 0.0],
            [-117.669934142677945, 33.520883796123655, 0.0],
            [-117.669934219896732, 33.52088381481029, 0.0],
            [-117.669934297846424, 33.5208838312303, 0.0],
            [-117.669934376432224, 33.520883845363748, 0.0],
            [-117.669934455558618, 33.520883857193397, 0.0],
            [-117.669934535129315, 33.520883866704906, 0.0],
            [-117.669934615047609, 33.52088387]
          ]
        ]
      }
    }
  ]
}
```
