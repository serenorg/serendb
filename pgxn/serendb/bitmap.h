#ifndef SERENDB_BITMAP_H
#define SERENDB_BITMAP_H

/*
 * Utilities for manipulating bits8* as bitmaps.
 */

#define BITMAP_ISSET(bm, bit) ((bm)[(bit) >> 3] & (1 << ((bit) & 7)))
#define BITMAP_SET(bm, bit) (bm)[(bit) >> 3] |= (1 << ((bit) & 7))
#define BITMAP_CLR(bm, bit) (bm)[(bit) >> 3] &= ~(1 << ((bit) & 7))

#endif							/* SERENDB_BITMAP_H */
