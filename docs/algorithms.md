# Luthier — algorithm research (state of the art)

This document surveys **algorithm and library choices** for each layer of the
luthier algorithm stack defined in [architecture.md §9](architecture.md#9-algorithm-stack).
It complements [decisions.md](decisions.md) (M1 defaults) with a broader research
catalog: pros/cons, bibliography, and open-source implementations.

**How to read this document**

| Column / field | Meaning |
| --- | --- |
| **Reference** | Primary paper or canonical report (DOI / arXiv / project page) |
| **Packages** | Libraries with **repository URLs**; Python-first where possible |
| **Maturity** | Community adoption, maintenance, academic/industrial pedigree |
| **luthier fit** | Rough suitability for M1 (sparse), M2 (dense), or future milestones |

**Selection principles (luthier)**

1. Prefer **consolidated** codebases from universities, research labs, or long-maintained OSS foundations (ETH, INRIA, Google, OpenCV, OSGeo, etc.).
2. Prefer **composable blocks** (detector + matcher + BA) over monoliths when we need testable boundaries — unless a monolith is clearly superior (COLMAP).
3. Python bindings (`pip`) are ideal; C/C++ cores wrapped via **pybind11** / **ctypes** are acceptable (pycolmap model).
4. Learned methods are listed for completeness; classical + COLMAP stack remains the **M1 baseline** per AD-03.

---

## Integrated photogrammetry pipelines

These bundles span several layers. They are the usual starting points when building
a production SfM/MVS system.

| Pipeline | Origin | Covers (layers) | Reference | Repository | Pros | Cons |
| --- | --- | --- | --- | --- | --- | --- |
| **COLMAP** | ETH Zurich | Features → dense MVS → export | [Schönberger & Frahm, 2016](https://doi.org/10.1109/CVPR.2016.563); [Schönberger et al., 2016 MVS](https://doi.org/10.1109/CVPR.2016.564) | [colmap/colmap](https://github.com/colmap/colmap) | De-facto research & industry standard; incremental & global SfM; patch-match MVS; excellent docs | C++ core; heavy GPU option for MVS; API surface large |
| **pycolmap** | COLMAP team | Python API to COLMAP | Same as COLMAP | [colmap/pycolmap](https://github.com/colmap/pycolmap) | Official bindings; pip wheels on many platforms; **M1 default (AD-03)** | Tied to COLMAP release cycle; some features lag CLI |
| **OpenMVG** | Mikros Image / community | Features → global SfM → export | [Moulon et al., 2016](https://doi.org/10.1007/s11263-015-0828-3) | [openMVG/openMVG](https://github.com/openMVG/openMVG) | Modular “open Multiple View Geometry”; strong global SfM; clean CLI | Sparse-focused; dense via external OpenMVS; smaller ecosystem than COLMAP |
| **OpenMVS** | cDc | Dense MVS from OpenMVG/COLMAP | [cDc, 2015 technical report](https://cdcseacave.github.io/openMVS/) | [cdcseacave/openMVS](https://github.com/cdcseacave/openMVS) | High-quality dense mesh/cloud; integrates with COLMAP/OpenMVG | Separate pipeline step; C++ build |
| **AliceVision / Meshroom** | AliceVision (INRIA, etc.) | IO → features → SfM → MVS → mesh | [AliceVision overview](https://alicevision.org/) | [alicevision/AliceVision](https://github.com/alicevision/AliceVision); [alicevision/Meshroom](https://github.com/alicevision/Meshroom) | INRIA-backed; node-graph UI; production node-based CLI | Large dependency tree; less “library-first” than pycolmap |
| **OpenSfM** | Mapillary (Meta) | Features → incremental SfM | [Mapillary OpenSfM docs](https://opensfm.org/docs/) | [mapillary/OpenSfM](https://github.com/mapillary/OpenSfM) | Python-native; map/GPS priors; good for street-scale | Less maintained post-Mapillary; weaker dense MVS than COLMAP |
| **TheiaSfM** | Google / community | Global SfM, BA | [Wilson & Snavely, 2014](https://doi.org/10.1007/s11263-013-0721-3) | [sweeneychris/TheiaSfM](https://github.com/sweeneychris/TheiaSfM) | Clean C++ API; strong global solvers; Ceres integration | Smaller community; sparse only |
| **hloc** | ETH Zurich | Learned features + matching + COLMAP export | [Sarlin et al., 2019](https://doi.org/10.1109/CVPR.2019.00211); [Sarlin et al., 2020](https://arxiv.org/abs/1911.11763) | [cvg/Hierarchical-Localization](https://github.com/cvg/Hierarchical-Localization) | SOTA localization & challenging pairs; COLMAP-compatible export | PyTorch GPU; research code layout; ops overhead |
| **GLOMAP** | ETH Zurich | Fast global SfM (COLMAP successor path) | [Pan et al., 2024](https://arxiv.org/abs/2408.16293) | [colmap/glomap](https://github.com/colmap/glomap) | Orders-of-magnitude faster global mapping; COLMAP ecosystem | Newer; dense/color still via COLMAP |
| **nerfstudio / COLMAP export** | Berkeley | SfM front-end for NeRF | [Tancik et al., 2023](https://doi.org/10.1145/3588432.3591516) | [nerfstudio-project/nerfstudio](https://github.com/nerfstudio-project/nerfstudio) | Modern NVS workflows | Overkill for point-cloud PLY product |

---

## 1. IO layer — input preparation

Maps to [architecture §9.3.1](architecture.md#931-io-layer--input-preparation).

### 1.1 Image discovery and validation

| Approach | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Directory enumeration + suffix filter** | — (stdlib pattern) | Python `pathlib` (built-in) | Zero deps; deterministic | No content sniffing |
| **MIME / magic-byte validation** | — | [python-magic](https://github.com/ahupp/python-magic) → [file/file](https://github.com/file/file) | Catches misnamed files | Extra native dep |
| **Pillow verify** | [Clark, Pillow docs](https://pillow.readthedocs.io/) | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | Pure-Python wheel; widely trusted | Slower on huge batches |

**luthier today:** `pathlib` discovery ([`io.images`](../src/luthier/io/images.py)); Pillow/OpenCV optional for decode.

### 1.2 Raster decode and color space

| Approach | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **OpenCV `imread`** | [Bradski, 2000 Dr. Dobb's](https://opencv.org/) | [opencv/opencv](https://github.com/opencv/opencv); [opencv-python](https://github.com/opencv/opencv-python) | Fast; BGR layout; COLMAP ecosystem default | BGR vs RGB footguns |
| **Pillow decode** | [Pillow](https://pillow.readthedocs.io/) | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | Excellent format coverage (TIFF, etc.) | Slower than OpenCV for JPEG |
| **libvips (pyvips)** | [Keskinen et al., 2019](https://doi.org/10.1109/ICIP.2019.8802936) (streaming) | [libvips/libvips](https://github.com/libvips/libvips); [libvips/pyvips](https://github.com/libvips/pyvips) | Low memory on gigapixel TIFFs | Less common in SfM tutorials |
| **tifffile / imagecodecs** | TIFF spec | [cgohlke/tifffile](https://github.com/cgohlke/tifffile); [cgohlke/imagecodecs](https://github.com/cgohlke/imagecodecs) | Scientific TIFF + compression codecs | Niche |
| **rawpy (RAW DSLR)** | [LibRaw](https://www.libraw.org/) | [letmaik/rawpy](https://github.com/letmaik/rawpy) | Demosaic CR2/NEF | Needs LibRaw binary |

### 1.3 EXIF / metadata extraction

| Approach | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **EXIF focal length & sensor** | [JEITA EXIF 2.32](https://www.cipa.jp/std/documents/e/DC-008-Translation-2019-E.pdf) | [ianare/exif-py](https://github.com/ianare/exif-py); [ExifTool](https://exiftool.org/) | Initial camera intrinsics prior for SfM | Missing/wrong EXIF common on phones |
| **OpenCV Photo metadata** | OpenCV docs | [opencv/opencv](https://github.com/opencv/opencv) | Same stack as decode | Limited vs ExifTool |

### 1.4 Radiometric preprocessing (optional IO)

| Approach | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Histogram equalization / CLAHE** | [Pizer et al., 1987](https://doi.org/10.1109/TMI.1987.634387) | OpenCV `createCLAHE` | Helps feature detection on flat lighting | Can break color fidelity |
| **Vignetting correction** | [Goldman, 2010 (TPAMI)](https://doi.org/10.1109/TPAMI.2010.55) | OpenCV; custom | Consistent appearance across frame | Needs calibration or EXIF |
| **Undistortion (pre-SfM)** | Brown–Conrady model | OpenCV `undistort`; COLMAP internally | Straight lines for detectors | Usually deferred to SfM intrinsics estimation |

### 1.5 Video → frame `ImageSet` (future)

| Approach | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Uniform frame sampling** | — | [FFmpeg](https://ffmpeg.org/); [imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | Simple; industry standard | Motion blur, redundancy |
| **FFmpeg scene-change filter** | FFmpeg `select` filter | [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Fewer redundant frames | Tuning per video |
| **Optical-flow keyframe picking** | [Baker & Matthews, 2004](https://doi.org/10.1023/B:VISI.0000011205.39205.f3) | OpenCV optical flow | Better baseline diversity | Compute cost |
| **SLAM keyframe policies** | [Mur-Artal et al., 2015 ORB-SLAM](https://doi.org/10.1109/TRO.2015.2463673) | [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) | Proven for VO | Full SLAM overkill for offline SfM |
| **COLMAP sequential matcher** | COLMAP docs | pycolmap | Built for video-like sequences | Still needs frame extraction first |

### 1.6 Remote sync / golden datasets (operational IO)

| Approach | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **HTTP fetch + checksum** | — | `urllib`; [requests](https://github.com/psf/requests) | Simple golden sync | Manual manifest |
| **rclone** | — | [rclone/rclone](https://github.com/rclone/rclone) | S3/GDrive/Dropbox unified | External binary |
| **DVC** | [Iter.ai DVC paper](https://dvc.org/doc/user-guide/project-structure) | [iterative/dvc](https://github.com/iterative/dvc) | Reproducible dataset versioning | Ops complexity |
| **COLMAP sample data** | COLMAP dataset page | [colmap/colmap](https://github.com/colmap/colmap) (`scripts/shell/fetch_*`) | Trusted benchmark imagery | Fixed scenes only |

---

## 2. Feature extraction layer

Maps to [architecture §9.3.2](architecture.md#932-feature-extraction-layer).

### 2.1 Classical local features (detect + describe)

| Detector / descriptor | Reference | Dim | Packages | Pros | Cons |
| --- | --- | --- | --- | --- | --- |
| **SIFT** | [Lowe, 2004](https://doi.org/10.1109/CVPR.2004.1285544) | 128 | OpenCV (patent-free since 2020); [vlfeat/vlfeat](https://github.com/vlfeat/vlfeat) | Gold standard accuracy; scale invariant | Slower; patented history |
| **SURF** | [Bay et al., 2008](https://doi.org/10.1016/j.cviu.2007.09.003) | 64/128 | OpenCV; VLFeat | Faster than SIFT | Weak on weak texture |
| **ORB** | [Rublee et al., 2011](https://doi.org/10.1109/ICCV.2011.6126544) | 32 (binary) | OpenCV | Very fast; free | Less discriminative; more outliers |
| **AKAZE** | [Alcantarilla et al., 2013](https://doi.org/10.1007/s11263-012-0590-3) | 61 (MLDB) | OpenCV; [pablofdezalc/akaze](https://github.com/pablofdezalc/akaze) | Good speed/quality | Tuning-sensitive |
| **BRISK** | [Leutenegger et al., 2011](https://doi.org/10.1109/ICCV.2011.6126638) | 512-bit | OpenCV | Fast binary | Lower precision than SIFT |
| **KAZE / AKAZE family** | Nonlinear scale space | — | OpenCV | Strong on blur | Heavier compute |
| **DAISY** | [Tola et al., 2010 (TPAMI)](https://doi.org/10.1109/TPAMI.2009.77) | variable | OpenCV | Dense-friendly | Less common in SfM |
| **RootSIFT** | [Arandjelović & Zisserman, 2012](https://doi.org/10.1109/CVPR.2012.6248018) | 128 | OpenCV (normalize SIFT) | Big matcher boost | Still need SIFT |
| **FREAK** | [Alahi et al., 2012](https://doi.org/10.1109/CVPR.2012.6247916) | 512-bit | OpenCV | Fast retina-inspired | Superseded by learned |
| **BRIEF / CMT etc.** | [Calonder et al., 2010](https://doi.org/10.1109/CVPR.2010.5539973) | binary | OpenCV | Minimal | Weak for wide baseline |

**COLMAP default:** SIFT (often via VLFeat or covariant SIFT in newer COLMAP).

### 2.2 Covariant / affine-covariant features

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Hessian-Affine + SIFT** | [Mikolajczyk & Schmid, 2004](https://doi.org/10.1109/CVPR.2004.1285546) | VLFeat; COLMAP | Handles strong viewpoint change | Slow |
| **SIFT++ / DSP-SIFT** | [Dong & Soatto, 2015](https://doi.org/10.1109/CVPR.2015.7298993) | Research code | Better repeatability | Not in default COLMAP |
| **Key.Net** | [Barroso-Laguna et al., 2019 (ICCV)](https://arxiv.org/abs/1904.00889) | [axelBarroso/Key.Net](https://github.com/axelBarroso/Key.Net) | Learned covariant | GPU; training domain bias |

### 2.3 Learned local features (GPU)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **SuperPoint** | [DeTone et al., 2018](https://arxiv.org/abs/1712.07684) | [magicleap/SuperPointPretrainedNetwork](https://github.com/magicleap/SuperPointPretrainedNetwork); hloc | Repeatable; homography-friendly | GPU; domain shift outdoors |
| **R2D2** | [Revaud et al., 2019 (NeurIPS)](https://arxiv.org/abs/1906.06195) | [naver/r2d2](https://github.com/naver/r2d2) | Reliable detectors | Heavy |
| **DISK** | [Tyszkiewicz et al., 2020 (NeurIPS)](https://arxiv.org/abs/2006.13566) | [cvlab-epfl/disk](https://github.com/cvlab-epfl/disk); kornia | Strong accuracy | GPU |
| **ALIKED** | [Zhang et al., 2023 (IEEE TIM)](https://arxiv.org/abs/2304.03608) | [Shiaoming/ALIKED](https://github.com/Shiaoming/ALIKED) | Fast learned; good efficiency | Newer |
| **XFeat** | [Potje et al., 2024](https://arxiv.org/abs/2404.19174) | [verlab/accelerated_features](https://github.com/verlab/accelerated_features) | Real-time; CPU-friendly learned | Less tested vs COLMAP defaults |
| **SIFT + LightGlue (detector-free pairing)** | Uses SuperPoint etc. | hloc | End-to-end tuned | Torch stack |

**Aggregator library:** [kornia/kornia](https://github.com/kornia/kornia) implements several detectors/descriptors in PyTorch.

### 2.4 Regions of interest / segmentation (optional)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Mask R-CNN** | [He et al., 2017](https://doi.org/10.1109/CVPR.2017.322) | [facebookresearch/detectron2](https://github.com/facebookresearch/detectron2) | Object masks exclude sky/people | Needs GPU; slow |
| **SAM** | [Kirillov et al., 2023](https://doi.org/10.1109/CVPR.2023.00383) | [facebookresearch/segment-anything](https://github.com/facebookresearch/segment-anything) | Flexible masks | Heavy; overkill M1 |
| **Simple sky / saliency heuristics** | Classical | OpenCV thresholding | Cheap sky rejection | Fragile |

### 2.5 Feature extraction backends (consolidated)

| Backend | Repository | Notes |
| --- | --- | --- |
| **COLMAP / pycolmap SIFT** | [colmap/pycolmap](https://github.com/colmap/pycolmap) | `extract_features` — **default M1 path** |
| **OpenCV** | [opencv/opencv](https://github.com/opencv/opencv) | ORB/AKAZE/SIFT for custom pipelines |
| **VLFeat** | [vlfeat/vlfeat](https://github.com/vlfeat/vlfeat) | Reference SIFT implementation |
| **OpenMVG** | [openMVG/openMVG](https://github.com/openMVG/openMVG) | `openMVG_main_ComputeFeatures` |
| **AliceVision** | [alicevision/AliceVision](https://github.com/alicevision/AliceVision) | Multiple preset feature pipelines |
| **hloc extractors** | [cvg/Hierarchical-Localization](https://github.com/cvg/Hierarchical-Localization) | SuperPoint, DISK, etc. → export to COLMAP DB |

---

## 3. Optimization layer

Maps to [architecture §9.3.3](architecture.md#933-optimization-layer). Sub-stages:
**retrieval → matching → geometric verification → SfM → bundle adjustment →
triangulation → (dense MVS) → color propagation**.

### 3.1 Image retrieval (pair selection)

Avoids O(N²) matching on large sets.

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Exhaustive pairs** | — | COLMAP `exhaustive_matcher` | Simple; best for N < ~200 | Quadratic cost |
| **Sequential / vocabulary tree** | [Nister & Stewenius, 2006](https://doi.org/10.1109/CVPR.2006.264) | COLMAP vocab tree; [openMVG/openMVG](https://github.com/openMVG/openMVG) | Scales to large collections | Needs vocabulary training |
| **NetVLAD / AP-GeM retrieval** | [Arandjelović et al., 2016](https://doi.org/10.1109/CVPR.2016.572) | hloc retrieval models | Strong learned retrieval | GPU; model weights |
| **CosPlace / EigenPlaces** | [Berton et al., 2022](https://doi.org/10.1109/CVPR.2022.01024) | hloc | Outdoor place recognition SOTA | Domain-specific |
| **GPS / time proximity** | — | OpenSfM | Great for mapping data | Needs metadata |

### 3.2 Feature matching

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Brute-force + L2 / Hamming** | — | OpenCV `BFMatcher`; COLMAP | Exact; simple | Slow at scale |
| **FLANN (k-d tree, LSH)** | [Muja & Lowe, 2014](https://doi.org/10.1109/CVPR.2014.156) | OpenCV FLANN; COLMAP | Fast approximate NN | Parameter tuning |
| **Mutual nearest neighbor** | Common practice | COLMAP | Reduces false matches | Still many outliers |
| **Lowe ratio test** | [Lowe, 2004](https://doi.org/10.1109/CVPR.2004.1285544) | COLMAP; OpenCV | Classic filter | Fixed threshold fragile |
| **Cross-check + symmetric** | — | OpenCV | Easy win | — |
| **SuperGlue** | [Sarlin et al., 2020](https://arxiv.org/abs/1911.11763) | [magicleap/SuperGluePretrainedNetwork](https://github.com/magicleap/SuperGluePretrainedNetwork); hloc | Learned graph matcher; handles weak texture | GPU; slower than ratio test |
| **LightGlue** | [Lindenberger et al., 2023](https://doi.org/10.1109/ICCV.2023.00837) | [cvg/LightGlue](https://github.com/cvg/LightGlue) | Faster than SuperGlue; adaptive depth | GPU |
| **LoFTR** | [Sun et al., 2021](https://doi.org/10.1109/CVPR.2021.00947) | [zju3dv/LoFTR](https://github.com/zju3dv/LoFTR) | Detector-free; good on textureless | Dense matches; memory |
| **DUSt3R / MASt3R** | [Wang et al., 2023 (DUSt3R)](https://arxiv.org/abs/2312.14132); [Leroy et al., 2024 (MASt3R)](https://arxiv.org/abs/2406.09756) | [naver/dust3r](https://github.com/naver/dust3r); [naver/mast3r](https://github.com/naver/mast3r) | Direct 3D-oriented matching | Different pipeline paradigm |
| **COLMAP guided matching** | Epipolar constraints | pycolmap | Uses known poses to refine | Post-initial SfM |

### 3.3 Geometric verification (two-view)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **RANSAC + fundamental matrix** | [Fischler & Bolles, 1981](https://doi.org/10.1145/358669.358692); [Hartley & Zisserman, 2004](https://doi.org/10.1017/CBO9780511811685) | COLMAP; OpenCV `findFundamentalMat` | Standard uncalibrated filter | Needs enough parallax |
| **RANSAC + essential matrix** | Hartley & Zisserman | COLMAP; OpenCV | Calibrated cameras | Needs intrinsics estimate |
| **RANSAC + homography** | Hartley & Zisserman | COLMAP | Planar / rotational motion | Wrong model hurts 3D |
| **MAGSAC++** | [Barath et al., 2020 (CVPR)](https://arxiv.org/abs/1912.05909) | [danini/magsac](https://github.com/danini/magsac); OpenCV contrib | Better threshold-free scoring | Contrib build |
| **DEGENSAC** | [Chum et al., 2005](https://doi.org/10.1109/CVPR.2005.47) | OpenCV | Degeneracy awareness | Less exposed in COLMAP |
| **LO-RANSAC** | [Chum et al., 2003](https://doi.org/10.1023/A:1024407627248) | COLMAP internal | Local optimization RANSAC | — |

### 3.4 Structure from Motion (multi-view)

#### Incremental SfM

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Incremental SfM (COLMAP)** | [Schönberger & Frahm, 2016](https://doi.org/10.1109/CVPR.2016.563) | [colmap/pycolmap](https://github.com/colmap/pycolmap) | Robust; well tested; **M1 default** | Order-dependent; drift on loop-free paths |
| **Bundler** | [Snavely et al., 2006](https://doi.org/10.1145/1141911.1141964) | [snavely/bundler_sfm](https://github.com/snavely/bundler_sfm) | Historical reference | Obsolete vs COLMAP |
| **VisualSfM** | [Wu, 2013](http://ccwu.me/vsfm/) | [ccwu/vsfm](https://github.com/ccwu/vsfm) | Fast desktop tool | Unmaintained |
| **OpenMVG incremental** | OpenMVG | [openMVG/openMVG](https://github.com/openMVG/openMVG) | Modular | Less default than COLMAP |

#### Global SfM

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Global SfM (rotation averaging + translation)** | [Moulon et al., 2013](https://doi.org/10.1109/ICCV.2013.241) | OpenMVG; COLMAP `global_mapper` | Handles loop closure better | Sensitive to outliers |
| **L1 rotation averaging** | [Chatterjee & Govindu, 2013](https://doi.org/10.1109/ICCV.2013.241) | TheiaSfM | Theoretically robust | — |
| **GLOMAP** | [Pan et al., 2024](https://arxiv.org/abs/2408.16293) | [colmap/glomap](https://github.com/colmap/glomap) | Very fast global pipeline | New |
| **Theia global reconstruction** | [Wilson & Snavely, 2014](https://doi.org/10.1007/s11263-013-0721-3) | [sweeneychris/TheiaSfM](https://github.com/sweeneychris/TheiaSfM) | Clean global solvers | Smaller community |

#### SLAM / VO hybrids (video, low POV)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **ORB-SLAM3** | [Campos et al., 2021](https://doi.org/10.1109/TRO.2021.3075644) | [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) | Real-time; monocular | Scale ambiguity mono; map vs SfM export |
| **DROID-SLAM** | [Teed & Deng, 2021](https://doi.org/10.1007/s11263-021-01470-4) | [princeton-vl/DROID-SLAM](https://github.com/princeton-vl/DROID-SLAM) | Dense learned VO | GPU; different output contract |
| **COLMAP sequential + video frames** | COLMAP | pycolmap | Offline; same PLY path | No temporal smoothness prior |

### 3.5 Bundle adjustment (BA)

| Solver | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Ceres Solver** | [Agarwal et al., Ceres Solver](https://ceres-solver.org/) | [ceres-solver/ceres-solver](https://github.com/ceres-solver/ceres-solver) | Industry standard non-linear least squares | C++ lib; used inside COLMAP |
| **g2o** | [Kümmerle et al., 2011](https://doi.org/10.1109/ICRA.2011.5979944) | [RainerKuemmerle/g2o](https://github.com/RainerKuemmerle/g2o) | Graph optimization framework | Lower-level |
| **GTSAM** | [Dellaert & Gtsam, 2012](https://doi.org/10.1007/978-3-642-34046-5_32) | [borglab/gtsam](https://github.com/borglab/gtsam) | Factor graphs; strong docs | Different API culture |
| **COLMAP BA** | Schönberger 2016 | pycolmap | Integrated; rad/distortion models | Black box unless configured |
| **OpenMVG BA** | Moulon 2016 | OpenMVG | Modular | — |
| **Theia BA** | Wilson 2014 | TheiaSfM | Ceres-backed | — |

**BA variants (configured inside COLMAP / Ceres):**

| Variant | Reference | Pros | Cons |
| --- | --- | --- | --- |
| **Local BA** | Incremental SfM standard | Fast | Drift without global passes |
| **Global BA** | Periodic full refine | Reduces accumulated error | Expensive on large scenes |
| **Rig BA (multi-camera)** | COLMAP rig docs | Insta360 / rigged cameras | Needs calibration |
| **Covariance / Schur complement** | Ceres internals | Efficient structure-from-motion normal equations | — |

### 3.6 Triangulation

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Linear triangulation (DLT)** | Hartley & Zisserman | COLMAP; OpenCV `triangulatePoints` | Simple | Not optimal statistically |
| **Mid-point (least squares)** | — | COLMAP | Better reprojection consistency | — |
| **Optimal triangulation** | [Hartley & Sturm, 1997](https://doi.org/10.1109/34.611822) | COLMAP | Minimizes reprojection error properly | Slightly heavier |
| **Angular error filtering** | COLMAP | pycolmap | Rejects ill-conditioned rays | Threshold tuning |

### 3.7 Dense reconstruction (M2 — optional optimization extension)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **COLMAP patch-match MVS** | [Schönberger et al., 2016](https://doi.org/10.1109/CVPR.2016.564) | [colmap/colmap](https://github.com/colmap/colmap) | Excellent quality; GPU option | CUDA path; memory |
| **OpenMVS** | cDc 2015 | [cdcseacave/openMVS](https://github.com/cdcseacave/openMVS) | Dense point cloud + mesh | Separate toolchain |
| **AliceVision MVS** | AliceVision | [alicevision/AliceVision](https://github.com/alicevision/AliceVision) | Integrated with Meshroom | Heavy |
| **PMVS/CMVS** | [Furukawa & Ponce, 2010 (TPAMI)](https://doi.org/10.1109/TPAMI.2009.161) | [pmoulon/CMVS-PMVS](https://github.com/pmoulon/CMVS-PMVS) | Classic | Superseded |
| **ACMH / ACMH-MVS** | [Xu & Tao, 2019](https://doi.org/10.1109/CVPR.2019.00540) | Research repos | Fast multi-hypothesis | Less packaging |
| **Neural MVS (MVSNet family)** | [Yao et al., 2018 (ECCV)](https://arxiv.org/abs/1804.02505) | [YoYo000/MVSNet](https://github.com/YoYo000/MVSNet) | Learned depth | GPU; needs training data match |

### 3.8 Color propagation (optimization sub-stage)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Single best view projection** | Common SfM practice | COLMAP point export | Fast | Viewing-angle artifacts |
| **Median / mean across observations** | — | COLMAP; custom numpy | Robust to specularities | Needs track visibility |
| **Weighted by incidence angle** | Shading models | Custom | Reduces grazing-angle blur | More code |
| **Bilinear texture sample** | Graphics standard | OpenCV `remap`; numpy | Sub-pixel color | Needs float images |
| **Dense patch color (MVS)** | Schönberger MVS 2016 | COLMAP dense | High-quality dense color | M2 scope |
| **Exposure compensation before sample** | [Goldman, 2010 (TPAMI)](https://doi.org/10.1109/TPAMI.2010.55) | OpenCV; OpenMVG radiometry | Consistent colors across exposures | Extra solve |
| **Learned appearance (NeRF-style)** | [Mildenhall et al., 2020](https://doi.org/10.1145/3386569.3392455) | nerfstudio etc. | View-dependent effects | Not sparse PLY friendly |

**M1 recommendation:** use **COLMAP / pycolmap** track colors (median RGB from
observing images) — satisfies [architecture §9.3.3](architecture.md#color-assignment--placement-decision).

---

## 4. Post-processing layer

Maps to [architecture §9.3.4](architecture.md#934-post-processing-layer).

### 4.1 Geometric outlier rejection

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Reprojection error threshold** | SfM standard | COLMAP filter; custom | Removes bad triangulations | Needs observation graph |
| **Statistical outlier removal (SOR)** | PCL convention | [PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl); [isl-org/Open3D](https://github.com/isl-org/Open3D) `remove_statistical_outlier` | Removes isolated noise | k-NN parameter |
| **Radius outlier removal** | PCL | Open3D; PCL | Simple density test | Fixed radius scale-dependent |
| **Voxel grid downsampling** | — | Open3D; PCL | Uniform density; smaller files | Loses detail (not strictly outlier) |
| **DBSCAN clustering** | [Ester et al., 1996](https://doi.org/10.1145/783921.782009) | [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) | Keeps largest cluster | Scale parameter |
| **MLS smoothing** | [Levin, 2003](https://doi.org/10.1145/882262.882270) | PCL `MovingLeastSquares` | Smooth surface | Can blur sharp edges |
| **COLMAP point filtering** | COLMAP docs | pycolmap export filters | Consistent with solve | Limited toggles via API |

### 4.2 Duplicate / merge

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Voxel hashing merge** | — | Open3D `voxel_down_sample` + average color | Simple | Quantized grid |
| **Fuzzy duplicate merge (distance + color)** | — | Custom numpy | Preserves thin structures | Tuning |

### 4.3 Radiometric post-refinement (optional)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Gain compensation between images** | [Brown & Lowe, 2007](https://doi.org/10.1109/CVPR.2007.383246) | OpenMVG `Global_Alignment` | Exposure harmonization | Needs overlap graph |
| **Bilateral filter on colors** | [Tomasi & Manduchi, 1998](https://doi.org/10.1109/ICCV.1998.710815) | Open3D | Denoise colors | Can smear boundaries |
| **Chrominance vs luminance separate** | Photo-zonography | OpenCV LAB space | Preserves edges | Manual pipeline |

### 4.4 Coordinate frame / scale (optional)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Similarity transform to GPS** | — | Open3D `registration`; OpenSfM | Geo-referenced output | Needs GPS tags |
| **Ground plane RANSAC** | — | Open3D `segment_plane` | Z-up alignment | Fails without ground |
| **Umeyama alignment** | [Umeyama, 1991](https://doi.org/10.1109/34.88573) | numpy / Open3D | Compare to golden reference | Needs reference cloud |

**Post-processing library summary**

| Library | Repository | Python access |
| --- | --- | --- |
| **Open3D** | [isl-org/Open3D](https://github.com/isl-org/Open3D) | `pip install open3d` — **recommended for M1 filters** |
| **PCL** | [PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl) | [strawlab/python-pcl](https://github.com/strawlab/python-pcl) (often brittle); C++ primary |
| **PDAL** | [PDAL/PDAL](https://github.com/PDAL/PDAL) | [hobuinc/pdal-python](https://github.com/hobuinc/pdal-python) — GIS/LiDAR oriented |
| **numpy/scipy** | — | Custom statistical filters |

---

## 5. Output layer

Maps to [architecture §9.3.5](architecture.md#935-output-layer).

### 5.1 Point cloud serialization formats

| Format | Reference / spec | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **PLY (binary LE)** | [Ply spec](https://paulbourke.net/dataformats/ply/); luthier [spec §5](specification.md#5-output-specification--point-cloud-format) | stdlib `struct` (M1); [PointCloudLibrary/pcl](https://github.com/PointCloudLibrary/pcl) | CloudCompare native; human-readable ASCII variant | No CRS metadata |
| **PCD** | [PCL PCD](https://pointclouds.org/documentation/tutorials/pcd_file_format.html) | Open3D; PCL | PCL ecosystem | Less universal than PLY |
| **LAS / LAZ** | [ASPRS LAS](https://www.asprs.org/divisions-committees/lidar-division/laser-las-file-format) | [laspy/laspy](https://github.com/laspy/laspy); [LAStools/LAStools](https://github.com/LAStools/LAStools) | GIS standard; compression (LAZ) | Overkill for RGB meshes |
| **E57** | [ASTM E57](https://www.astm.org/e2807-11.html) | [asmwarrior/e57format](https://github.com/asmwarrior/e57format) | Rich metadata | Heavy |
| **XYZ / CSV** | — | stdlib | Debugging | Large; no color standard |
| **glTF / 3D Tiles** | [Khronos glTF](https://www.khronos.org/gltf/) | [KhronosGroup/glTF-Sample-Models](https://github.com/KhronosGroup/glTF-Sample-Models) | Web viewers | Not traditional point cloud tools |

### 5.2 Writers (implementations)

| Library | Repository | Notes |
| --- | --- | --- |
| **luthier `output.serialize`** | this repo | Contract owner — binary PLY per spec |
| **Open3D `write_point_cloud`** | [isl-org/Open3D](https://github.com/isl-org/Open3D) | PLY/PCD/XYZ; good reference impl |
| **trimesh** | [mikedh/trimesh](https://github.com/mikedh/trimesh) | PLY export; mesh-oriented |
| **plyfile** | [dranjan/python-plyfile](https://github.com/dranjan/python-plyfile) | Pure Python PLY read/write |
| **pyntcloud** | [daavoo/pyntcloud](https://github.com/daavoo/pyntcloud) | DataFrame-centric PLY |
| **laspy** | [laspy/laspy](https://github.com/laspy/laspy) | M4 LAS/LAZ candidate |

### 5.3 Compression (future)

| Method | Reference | Packages | Pros | Cons |
| --- | --- | --- | --- | --- |
| **Draco for point clouds** | [Google Draco](https://google.github.io/draco/) | [google/draco](https://github.com/google/draco) | Web streaming | Lossy |
| **LAZ (laszip)** | [laszip](https://laszip.org/) | LAStools / laspy | GIS standard lossless | Schema mapping from PLY |

---

## 6. Cross-cutting: binding C++ libraries to Python

When no mature `pip` package exists, luthier may follow the **pycolmap** pattern:

| Tool | Repository | Use |
| --- | --- | --- |
| **pybind11** | [pybind/pybind11](https://github.com/pybind/pybind11) | COLMAP, GLOMAP, custom C++ nodes |
| **nanobind** | [wjakob/nanobind](https://github.com/wjakob/nanobind) | Lighter binding alternative |
| **ctypes / cffi** | — | C API libraries (FFmpeg, libraw) |
| **subprocess CLI** | — | COLMAP binary, OpenMVG, OpenMVS, AliceVision — fallback per AD-03 |

---

## 7. Recommended defaults for luthier

Aligned with [decisions.md AD-03](decisions.md#ad-03--sfm-backend-was-od-03) and
[architecture §9](architecture.md#9-algorithm-stack).

| Layer | M1 default | M2 / future alternatives |
| --- | --- | --- |
| **IO** | `pathlib` + OpenCV/Pillow decode | FFmpeg keyframes; ExifTool; DVC sync |
| **Features** | COLMAP SIFT via **pycolmap** | SuperPoint + LightGlue (hloc); AKAZE for speed |
| **Matching** | COLMAP exhaustive/sequential + ratio test | LightGlue; vocab tree at scale |
| **Verification** | COLMAP RANSAC (F/E/H) | MAGSAC++ |
| **SfM** | COLMAP **incremental_mapper** | GLOMAP global; OpenMVG global |
| **BA** | Ceres inside COLMAP | — |
| **Triangulation** | COLMAP optimal | — |
| **Dense** | — (sparse only M1) | COLMAP patch-match or OpenMVS |
| **Color** | COLMAP track median RGB | Angle-weighted; radiometric refine |
| **Post-process** | Reprojection filter (COLMAP) + Open3D SOR | Voxel merge; DBSCAN |
| **Output** | stdlib binary PLY | Open3D reference; laspy (M4) |

### Suggested evaluation order when swapping algorithms

1. **Golden acceptance** — COLMAP South Building ([`tests/data/golden`](../tests/data/golden/)).
2. **Point count & reprojection error** — regression thresholds in CI.
3. **Visual inspection** — CloudCompare (AD-05).
4. **Runtime & memory** — document in PR when changing backends.

---

## 7b. Implementation & integration readiness

This section answers two questions for an implementer: *do the chosen algorithms
have a concrete, installable Python path?* and *does the documentation set give
everything needed to implement and integrate luthier as a library and as a
client?*

### 7b.1 Per-layer implementation toolchain (M1 default path)

Each stage maps to a concrete package, install command, and the luthier
[stack slot](architecture.md#102-stackyml-schema) that selects it.

| Layer / slot | Package (M1) | Install | Minimal entry point |
| --- | --- | --- | --- |
| `io.discover` | stdlib `pathlib` | — | `luthier.io.discover_images` (implemented) |
| `io.decode` | `opencv-python-headless` | `pip install opencv-python-headless` | `cv2.imread` |
| `features.extractor` | `pycolmap` | `pip install pycolmap` | `pycolmap.extract_features` |
| `reconstruction.*` | `pycolmap` | `pip install pycolmap` | `pycolmap.match_exhaustive`, `pycolmap.incremental_mapping` |
| `reconstruction.coloring` | `pycolmap` + `numpy` | `pip install pycolmap numpy` | track colors from `pycolmap.Reconstruction` |
| `postprocess.outliers` | `open3d` (optional) | `pip install open3d` | `remove_statistical_outlier` |
| `output.serializer` | stdlib `struct` | — | `luthier.io.write_point_cloud` (contract defined) |

All M1 algorithm work runs through **pycolmap**, which ships binary wheels on
Linux/macOS/Windows for CPython 3.12 (project default; see AD-13), so no separate COLMAP build is
required for the default path ([AD-03](decisions.md#ad-03--sfm-backend-was-od-03),
[AD-04](decisions.md#ad-04--runtime-dependencies-m1)).

### 7b.2 Enabling the reconstruction dependencies

The runtime dependencies are specified ([spec §12](specification.md#12-dependencies-m1--approved))
but ship as a **commented-out optional extra** in `pyproject.toml` until the M1
PR, to keep the framework install light. The M1 implementation PR uncomments and
installs:

```bash
pip install -e ".[dev,reconstruction]"   # reconstruction = numpy, opencv, pycolmap
```

### 7b.3 Documentation coverage for implementation and integration

| Need | Covered by | Status |
| --- | --- | --- |
| What to build (requirements, acceptance) | [specification.md](specification.md) | ✅ |
| System/module design, layer contracts | [architecture.md](architecture.md) §1–§11 | ✅ |
| Algorithm choices + OSS libraries per layer | this document | ✅ |
| Resolved defaults and rationale | [decisions.md](decisions.md) AD-01 … AD-12 | ✅ |
| How to plug/swap algorithms | [architecture.md §10](architecture.md#10-config-driven-algorithm-stack), [README](../README.md#pluggable-algorithm-stack-design-guidelines) | ✅ |
| Test levels + traceability | [testing.md](testing.md) | ✅ |
| Library + CLI usage | [README](../README.md#python-api) | ✅ |
| Extending via plugins (entry points) | [architecture.md §11.2](architecture.md#112-algorithm-registration-and-discovery-new-interface) | ✅ |
| Method / contribution workflow | [CONTRIBUTING.md](../CONTRIBUTING.md) | ✅ |

**Conclusion:** the algorithm catalog is accurate and the documentation set is
sufficient to implement M1 and to integrate luthier both as a library and as a
client. The only deferred enablement is uncommenting the `reconstruction` extra
in `pyproject.toml` at M1 (§7b.2).

---

## 8. Master bibliography (quick index)

| ID | Citation | URL |
| --- | --- | --- |
| B-LOWE-2004 | Lowe, Distinctive Image Features, IJCV 2004 | [DOI](https://doi.org/10.1109/CVPR.2004.1285544) |
| B-SCHONBERGER-2016-SFM | Schönberger & Frahm, Structure-from-Motion Revisited, CVPR 2016 | [DOI](https://doi.org/10.1109/CVPR.2016.563) |
| B-SCHONBERGER-2016-MVS | Schönberger et al., Pixelwise View Selection, CVPR 2016 | [DOI](https://doi.org/10.1109/CVPR.2016.564) |
| B-MOULON-2016 | Moulon et al., OpenMVG, JMLR 2016 | [DOI](https://doi.org/10.1007/s11263-015-0828-3) |
| B-HARTLEY-2004 | Hartley & Zisserman, Multiple View Geometry | [DOI](https://doi.org/10.1017/CBO9780511811685) |
| B-CERES-2013 | Agarwal et al., Ceres Solver | [Ceres](https://ceres-solver.org/) |
| B-SARLIN-2020 | Sarlin et al., SuperGlue, CVPR 2020 | [DOI](https://arxiv.org/abs/1911.11763) |
| B-LINDENBERGER-2023 | Lindenberger et al., LightGlue, ICCV 2023 | [DOI](https://doi.org/10.1109/ICCV.2023.00837) |
| B-PAN-2024 | Pan et al., GLOMAP, 2024 | [arXiv](https://arxiv.org/abs/2408.16293) |
| B-WILSON-2014 | Wilson & Snavely, Robust Global Translations, ECCV 2014 | [DOI](https://doi.org/10.1007/s11263-013-0721-3) |
| B-FISCHLER-1981 | Fischler & Bolles, RANSAC, CACM 1981 | [DOI](https://doi.org/10.1145/358669.358692) |
| B-NISTER-2006 | Nister & Stewenius, Vocabulary Tree, CVPR 2006 | [DOI](https://doi.org/10.1109/CVPR.2006.264) |
| B-RUBLEE-2011 | Rublee et al., ORB, ICCV 2011 | [DOI](https://doi.org/10.1109/ICCV.2011.6126544) |
| B-ALCANTARILLA-2013 | Alcantarilla et al., AKAZE, IJCV 2013 | [DOI](https://doi.org/10.1007/s11263-012-0590-3) |
| B-DETONE-2018 | DeTone et al., SuperPoint | [arXiv](https://arxiv.org/abs/1712.07684) |
| B-YAO-2018 | Yao et al., MVSNet, ECCV 2018 | [arXiv](https://arxiv.org/abs/1804.02505) |
| B-ESTER-1996 | Ester et al., DBSCAN, KDD 1996 | [DOI](https://doi.org/10.1145/783921.782009) |

---

## 9. Document maintenance

When adding or changing algorithms in luthier:

1. Update this file with the chosen method and rejected alternatives rationale.
2. Update [decisions.md](decisions.md) if the choice is a project default.
3. Add or switch the entry in [`config/stack.yml`](../config/stack.yml).
4. Update [architecture.md §9](architecture.md#9-algorithm-stack) only if layer
   **contracts** change (not when swapping SIFT for AKAZE).
5. Add tests per [testing.md](testing.md) traceability matrix.

**Related documents:** [architecture.md](architecture.md) ·
[decisions.md](decisions.md) · [specification.md](specification.md) ·
[testing.md](testing.md)
