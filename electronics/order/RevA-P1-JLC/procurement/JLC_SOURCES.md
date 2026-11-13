# JLC preparation sources

Reviewed 2026-09-22. Public catalog identity checks, not an authenticated stock reservation or supplier acceptance. Individual part sources are recorded per line in `JLC_sourcing.csv`. No replacement MPNs were introduced.

- [JLC BOM format](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly): Comment, Designator and Footprint; CSV accepted. Extra manufacturer and MPN columns retained for exact matching.
- [JLC CPL format](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly): Designator, Mid X, Mid Y, Layer, Rotation; mm; positive counterclockwise. CAD-anchor to body-center corrections are explicit in the conversion report.
- [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities): Standard minimum manufacturing size 70 x 70 mm. An engineering-created panel is required for this narrow single board. Standard is the proposed quotation route; exact process acceptance remains open.
- [Via covering](https://jlcpcb.com/help/article/pcb-via-covering): select nonconductive epoxy fill followed by copper capping, not ink plugging or tenting.
- [Use own / sourced parts](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order): sourced parts must be available and selected in the account parts library for assembly.
- [BOM/CPL matching issues](https://jlcpcb.com/help/article/common-bom-and-cpl-matching-issues-and-explanations): shortages can require pre-order/global sourcing; attrition and minimum quantities can exceed placement quantities.
- [XIAO catalog listing](https://jlcpcb.com/partdetail/Seeed-102010448/C17209540): exact original module, SMD 21 x 17.8 mm, listed for SMT assembly. This does not validate this carrier's hidden joints or module revision.
- [C5 exact manufacturer part at DigiKey](https://www.digikey.com/en/products/detail/murata-electronics/GRM1885C1H470JA01D/586904): source candidate for Global Sourcing. Public searches did not establish an exact JLC/LCSC code; BOM field intentionally blank. No claim that the part is unavailable globally.

The 25 supplied C-codes include LCSC-only identity evidence and a TPS61041DBVR LCSC datasheet association. These are marked separately from direct JLC catalog evidence. JLC must verify those mappings in the order. No numerical stock or price estimates are included because public views are not a reliable account-specific availability guarantee.
