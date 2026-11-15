# A02 - Atlas pages 85-167: generator and console

Worker `/root/w01_a02`, wave 1, 2026-11-15. I personally read **all 83 assigned
pages**, directly from the form-feed extract; no older reading report substituted.
I read complete AGENTS.md/PLAN.md, session entry/checkpoint/assignments, relevant
recovery navigation, and actual generator/console sources. Only this note changed.

## Identities and actual checks

Checkout: `/workspace/scratch/116ca0948095/Hammond-B3-Organ`.
HEAD `138fca9af7feca46d10b0e2b65d891f4751a3904`;
tree `d26e7ca86197750629b5e6f85fc548e03a815dd8`.
Index empty; root's AGENTS/session records dirty. Remote configuration inspected;
no live remote query, build, commit or publication performed.

- PDF: `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 21,248,265 bytes,
  SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Extract: `/workspace/scratch/116ca0948095/atlas/atlas.txt`,
  SHA-256 `e6ed8ed76663a8f12c487ae1e4d3ab69facc36971df240a15b1ba36eeb22485d`.
- Range: `b"\f".join(extract_bytes.split(b"\f")[84:167])`, 209,912 bytes,
  SHA-256 `efaa4aed7f2ac18853ad348feafda0dc8153a6ccdd757827071ee8e8a13c16fc`.
  Footer check passed all 83 expected page numbers; `pdfinfo` confirmed 500 pages.
- PDF skill: personally inspected Poppler renders of **100, 116, 158, 166**.
  Page 116's contact timings are explicitly illustrative. Page 158 confirms
  input-side early divider loads and ground-referenced outputs. Page 166 omits
  the sixteenth traversal entry; current ScannerRotor already corrects it.
- Python 3.12.14: `python3 -B tests/test_compile_profile.py` passed **37/37**,
  **4.130 s**, exit 0. In-memory validation/compilation and six printed mapping
  rows passed. Canonical authoring hash:
  `49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`;
  compiled hash `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

## Complete reading conclusions

| Pages | Consequence |
| --- | --- |
| 85-90 | Mechanical timing, gap modulation and hum are distinct; rates do not establish depths. |
| 91-96 | Separate observations/profile/bank/history; explicit waveform boundary, units, domain and unknowns. |
| 97-102 | Repeated foldback, all 549 routes, distinct contacts despite shared-source collisions. |
| 103-108 | Shared phases, scalar harmonic oracle, independent bandwidth/interpolation/conversion budgets. |
| 109-114 | Nominal 3 dB amplitude law and coherent sum; physical taps/loading remain unmeasured. |
| 115-120 | Independent make/break histories; fractional switching before bandwidth reduction; proposed RMS gate. |
| 121-126 | Exclusive selectors are restricted models; Cancel preserves notes; modern memories are separate. |
| 127-132 | Shared percussion readiness follows ninth-contact elapsed history and saved note ownership. |
| 133-138 | Isolated RC products are hypotheses, not audible decay; return/attenuation/percussion remain distinct. |
| 139-144 | Pedal exceptions/nulls and shared sources persist; reactor/low-wheel spectra need acquisition. |
| 145-150 | Loaded expression and controller calibration differ; moving capacitance requires d(Cv)/dt. |
| 151-156 | One applied timeline; patches differ from checkpoints; channel modes retain scoped policies. |
| 157-167 | 18L/18C/19 outputs, 16 stators/9 terminals; loading, phase and physical evidence remain separate. |

## Source comparison and dependency-ready recommendation

`TonewheelBank`, `Profile`, `ContactBank`, `ConsoleModel`, `Percussion` and
`Engine` were inspected directly. Shared continuous sources, coherent contact
aggregation, retained banks, routing-only Cancel and shared readiness are present.
Stopped sample-rate migration already preserves source/contact/percussion state;
do not duplicate it. The profile/compiler explicitly freezes normalized sine v1;
no measured harmonics or complete gearing are available. No new core correctness
defect was demonstrated.

**Unowned M3 candidate: fractional contact-switching reference and bounded
prototype**, supported by pp. 115-120 and existing M3 acceptance contracts.
Current ContactBank resolves Boolean edges on host frames; Engine hard-switches
those contributions without fractional edges or antialias tails. This is an
acknowledged limitation, not a regression. Freeze acceptance before implementation:

1. Declare fractional timestamps, stable edge ordering, units, filters, latency,
   storage/event limits and reference convergence.
2. Evaluate source phase and switching before decimation. Cover peak/zero-crossing
   edges, make/break, close edges, collisions, partial reversal and held chords.
3. At 44.1/48/96 kHz, verify irregular partitions, silence/disconnected outputs,
   persistent tails, zero frames and transactional rejection.
4. Apply proposed normalized RMS **<=1e-4** to agreed nonzero synthetic fixtures;
   predeclare an absolute near-zero criterion and independently converge the oracle.
5. Measure bounded callback/resource behavior; preserve nominal PCM, all 47
   parameters and state readers. Keep physical-click claims and live integration open.

A01's independent harmonic-source proposal is also supported by pp. 93/104/107/141,
but this range supplies no calibrated coefficients. For root's possible modern
performance-memory work, pp. 126/155 require a separate software-memory namespace,
atomic validation, preserved inactive banks/profile identity, no resurrected notes,
and explicit live-load ownership/percussion-history semantics. Preserve B3CONTROLS4.

No C++/native suite, hardware acquisition, deadline or hosted qualification ran.
M6 FOH, native close, visual-deck and R4 ownership remain untouched.

## Source SHA-256

`src/TonewheelBank.cpp`: `ebc26e2e61cc88d5525e390abf3897ebeae38e652c13ea3ef02818b2b3849e0b`

`src/ContactBank.cpp`: `91747d963d6cec74b3be12549abd8e816f4c176ce172fba52f9cdbc593c6e9e1`

`src/Engine.cpp`: `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a`

`src/Percussion.cpp`: `823685b879fad12492f86bbf5e78294668ee9b0567c58c26ac0b44aa28b1390a`

`tools/compile_profile.py`: `2ca649de88a3f267970e4ed00fa6c08b7c234bffcc1b4c24b47a89be608fb2a8`

`tests/test_compile_profile.py`: `159ccbac0a8873f5ce17488064305a126c5a5e1f994a1fa524ab7c3f663d3ca7`

## Individual page-segment SHA-256

Each line is `page:hash` for `extract_bytes.split(b"\f")[page-1]`, preserving
original whitespace and excluding the form-feed delimiter.

```text
85:5a6f2fa4509d544b7943e6ef8d73b83845190cf9280e797b64fde82d0df31322
86:de5a2d2727fb25bef36590cd8eb411bc8caa88f377f14ac41537a325a0f1dfbe
87:b201daed4df9f5b9c65d8bde3331609d1c16034d28e594127079f6cd42772797
88:eb2d0aca1bd76fbc86f9ff50252396a75e86a546bc36eed177b48fd26e948cb6
89:4f20367ef4ffee24f9cf206da8a3651c29f865f3fbad5b6d3e081bb24b8fb4a3
90:777b4b2eacd2a249b5d8dbe1a68d07b0e5fc93fab6158ab714fbbcc57ea193b5
91:fade5747750bce58df26d8f10e81167dace5491afd931d9af04d453ef42ea5fa
92:e5abfc8373bf32370348a0133e2cb739df43dcabc7c99a24e834890bf779b8dd
93:9b74d007cd3c4c8071134860b664e1e4b281f07a7db64e09a664a7bcf736312e
94:37853ae8dc72c33ce3b1054c1c77ac8db7f4556695a8e1569973e363b9509c00
95:34d7e7dd2ce197ae70c7fd467239c981a20dc3e4f2ee55e0fe32f133728f9b1f
96:66477db53668142118a84dd1817e7d1240dd2d4417e4023e596922b5725ebce9
97:dbd34c57c74493dfb8da7439980a47d979f15146be0044ab72dc01d79a6407cc
98:134bc4571e99e9fb4302c98bbba113e059c49c3f75e1ddd6815c0f90cffb4171
99:8e9eeb25bbf123476d372b01232283021ec5c76bc9b92a98b180e9c17a969b41
100:edcf5922eb0da0f9a35b85b5e2f22ab38b183b2764e9dc848a670ef2307741f9
101:a79c6e9478e1c0abf3d39bea1a172ffc585eebcfd51373a3a84fbb580610b414
102:4215e19f016fee32a8bbc93455012a8f1cca5111d70d604aa8b8a8e3aaaf6976
103:872d4c7c688407dc07ea929c5385e1d8e72b29e23a36b645e597408264f668c5
104:11aaaae64241cffe60bfa247790ca111529968b28f7a276c845a6c57e410bd8c
105:a420c00641402374b54fce8e0c68a6590342ba16777fc2c30482e4270d8e2de3
106:ccfefb70194cfc8a18466b8f4fedfcb2e51810a30da19b4f5584b6211364904f
107:374af3730df55b3a6538b4c18af1e654b0d9c4b85b811966913e7266b51afdf9
108:b152a25e19a47f288be15f815f6b8152191d3c09e2a2d7aa56de477392c9ea42
109:5e74e1eae06f16cf4057c27cfa66e6d584b36d96e24d041a82b25926e6933628
110:e3a66fc2db73f53f69c5b3d625987adfd7353417ce215add1b19266eac242b6a
111:351df5d1d1afe9f5f067ae5abb6a8febc8bed300b2997cc5bf3d90d895e2364f
112:6fe0197e3fd82ecbc67b29f30fe0ba2367840b5de0f713050c92bc5bf399ea4b
113:2b110480f857b3847cbe23b61fbcc4e992986fd819a07df28f83323f94be96e5
114:6911f916f658a0db06e13679a69290e6a8013a9750de03dbc9cd6ca9e4afc2bd
115:ba2858a27393d0daebafbd46ee175762c27abfdad4832445a8902adfbef31b27
116:3a57b7b9cdfb82d255593579e56dea9b60cdf572fb7e062330cadc3d0f68217f
117:f7e9816ec5c34f5354d6f75882fb3075a6eec3330a579761671f25053bc70f4d
118:ea61eb8f95883d6cabffc5cde66bd8f158046cfd36a48bd3804adb12691e42ae
119:4d6602302b502243cdefa8b74eb992ae60af9ef608a7f8102ab37a9e75118677
120:899b0b5dd3db2dbcd2847d0c79d5b015402748a4ae02086d6852c90595664c47
121:8b41beff3dc9d3a0399246b60af967aa8f05cd8358d579a47a2dfc28beb08c8b
122:84fe8cfd2f26abf08f62d4a2046914d999124ea054058628b76523f474f034a8
123:8191f8873eb315fb89ad06464affd594a730d1a91de6bc56c05a914ab8d5e82f
124:ab59023785dbe56e066bb2289cef3b2b0cd58dc39d300248cfe20685731f6df9
125:fc86d5089e1ca8c4e7a70ea12cd01a9731b40c6bbf0725a04c1da71dac09bbf6
126:95f18fb67e5bcc79368b9b057491ebf5c58c8e8766bd091558d7b7b5da3d1900
127:842b6dbc863a5fc8d73027f03bc5b4961a4cbb454ace8f9638447914930d33e2
128:c3f12a8647cf0bb43df56130aa9c52d22f3e6141643bb359ac87ea0f850b687f
129:5facff54dd088d3b46a619ed86f1954808bd2706965c3ee634a7af983ec674c0
130:2dfeba32327a55d075d9fc8dc9c9b381c9af750c8a3555a1741b992a1d703024
131:6b01475d71ae6139d4e0fa7e9d70941ac876d4aafdb18026aaf508e4db729761
132:740d7b2f09eda4f99a9e77f2a3efc52523e300e8c7273a12e13d01908bc5dbea
133:e208adbad3ae76d96df2f6a8860216c6d7769d2309b55223827d30a68423d7bf
134:930b88758faf69fa34917f3ee413e387b26493e6c7447f7bbb6b3b224b74af50
135:7abfb488376b161ac9fe290b51eedea66637835fc306b8b30f274d66af33d480
136:ec394959355099a07e966a5f23bacaee1e75dba96e35eb270b2aa2121150faa4
137:fcd7397ee5c7a87f6f9be7d7e2c0d54e559da60d50a608ab3e26ece164849c8d
138:27aad18ececc05b20b0e597ea2dcb1a74a5a5933ca88e46689b3e6f4d12bb6ee
139:1621c073fbc2374e38690c1a09ff8a76de2a39e976188c98f36bd56364e0895e
140:909079e7b7cb1300fd05aceb720396f83a0f064016215f97a894ecc634e3675e
141:c73054fbbec4f006a481f2ba9ce453997e3bc2940bed607ac9577e7c99caac19
142:33381d85e455bb52fff7ba1e2ca578e96570f285ec0b7339ddf3a600044132a0
143:5a074effbb075a736e13cf4a528640c72ab08821678bfc9f01ce177f6bb3e607
144:d9fca1cfe7ec5cb7266cd1a2676ebfc569f461b11959b8804541b674043b008e
145:21cd2d9b52e18164f1421af229733162c430c9d8dc5278d61cf6c91b4ec6913f
146:7e06d3f4cffc1a4c0a60b0afc04d0718343951aa7c72f0d6cbee11a6779cbca8
147:fe98082922212d28cc4a77bbe8c1eef2f136e505856a18c0fb91cefa791d6292
148:325ef939444be48aad450c0972537f5b79ecce72708dd65f9d362a46ed029966
149:928c5537aa46d00dbdc5ede7ef4f216b66e8179664f5ed13478cdfa2a1a4b430
150:df86dee322f2fcf6d6953eb588b3ba3dc2e4bbabb12beb71c7d2a9a292f07056
151:11441c023c82e6822d95009f59f06fddf6b57960bd421a901591dde1e5d099f1
152:c5b261c070063a4291f8e9a3521b9b546045feef956d748b83a9d63301babae3
153:13c8c952e5ec2eeb93dd96e9d81313ad07b2c0d83f665d651203ab82affb8a9d
154:cc6111b28354f723861d886e7325267e275f6fb81855d73fa500ea79a5fa664d
155:a13477a6dc793ab7a8634627358b1fe8d14b185c35b7d6d2784c57162eb09752
156:3edcf3ab3c2e41c8a112fbeb1a89e2713c5164aa7280a304ac4170e5d1c937f9
157:1138d02261256221b6b21bd5bf770950eaf02f248e8127679cbf0ec07fa8bc19
158:2f4800bd3837fe1bccb347ecb0d3ae1afee67ef566b420a191cc4fe32bc83d41
159:3a9b7193c6358cb65684b2fd3f7ecd67e48df6b59dad4f014cb17183c73bc87f
160:8340f2bc63c4908975cbda4faa71ba3f3af847f37c986c958207ea8da806f898
161:a9553c839ceed534d3efd43b0adb695cf0e7d507392ebabee992f86c0bc07ead
162:fdd418cc96e828c4385f16e447ed056cb75fa0fb6548fb6544b9011f81af8a93
163:e0302a2361e1fc3822a6b2af0a1c13cab4de43329da711629fa701e8adfd672a
164:a43df326939b3d38c37b7acfaf79141530dd688c835f883a00ff1a176a11d8e7
165:c9a015f26799acc769c9dc404884671cdf32bc53f25d203df02eb9e6221b4843
166:67dbf8d57e608ca26989f39a582a7ca1752503a89dfee76333302dbfc17802cf
167:442012ca4fc766690b147ba0e6988d30255cbe429cd8de1bce912a73387f2ba7
```
