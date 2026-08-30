# Product Attribute Code Extension

## Size-only Variant Fallback Barcode

Barcodes use `[4-digit Serial][1-digit Size Value Code][3-digit Category Code][4-digit Color Code]`.

The Size-only fallback format is `SSSSVCCCXXXX`, with Color Code fixed to `0000`:

```text
0001 + 1 + 120 + 0000 = 000111200000
```

Existing Size + Color, Color-only, non-variant, and other barcode generation remains unchanged. Existing barcodes are not overwritten, and Internal References remain unchanged.
