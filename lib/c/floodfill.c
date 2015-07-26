#include <stdio.h>
#include <stdlib.h>

typedef struct {
   int red;
   int green;
   int blue;
   int alpha;
} color;

// Definint a linked list structure
struct node_st {
   int x;
   int y;
   struct node_st *next;
};
typedef struct node_st node;


// Functions
int getIndex(int x, int y, int w, int bpc);
color blend(color current, color replacement, int alpha);
char compareUsingImage(int x, int y, char image[], int w, int h, int bpc, color target);
char compareUsingColor(color current, color target);
color getColor(int index, char image[], int bpc);
color mkcolor(int red, char green, char blue, char alpha);
color imkcolor(int thecolor);
int floodfill(int x, int y, char image[], int w, int h, int bpc, int ireplacement);

/*
 * CODE STARTS HERE
 */
int floodfill(int x, int y, char image[], int w, int h, int bpc, int ireplacement) {
   // Replacement color
   color replacement = imkcolor(ireplacement);

   // Target color
   color target = getColor(getIndex(x, y, w, bpc), image, bpc);

   if (compareUsingColor(target, replacement) == (char)0xff)
      return 0;

   // Creating the list/stack
   node *list = (node*) malloc(sizeof(struct node_st));
   (*list).x = x;
   (*list).y = y;
   (*list).next = NULL;

   // The algorithm itself
   int iterations=0;
   while (list != NULL) {
      node *pointer_to_free = list;
      node current = *list;
      list = current.next;

      int index = getIndex(current.x, current.y, w, bpc);
      color current_color = getColor(index, image, bpc);
      int blending_alpha = compareUsingColor(current_color, target);
      if (blending_alpha != (char)0) {
         color result = blend(current_color, replacement, blending_alpha);
         image[index] = result.red;
         image[index + 1] = result.green;
         image[index + 2] = result.blue;
      }

      // Query neighbours...
      node *new;

      // North
      if (compareUsingImage(current.x, current.y-1, image, w, h, bpc, target)) {
         new = (node*) malloc(sizeof(struct node_st));
         (*new).x = current.x;
         (*new).y = current.y-1;
         (*new).next = list;
         list = new;
      }

      // South
      if (compareUsingImage(current.x, current.y+1, image, w, h, bpc, target)) {
         new = (node*) malloc(sizeof(struct node_st));
         (*new).x = current.x;
         (*new).y = current.y+1;
         (*new).next = list;
         list = new;
      }

      // West
      if (compareUsingImage(current.x-1, current.y, image, w, h, bpc, target)) {
         new = (node*) malloc(sizeof(struct node_st));
         (*new).x = current.x-1;
         (*new).y = current.y;
         (*new).next = list;
         list = new;
      }

      // East
      if (compareUsingImage(current.x+1, current.y, image, w, h, bpc, target)) {
         new = (node*) malloc(sizeof(struct node_st));
         (*new).x = current.x+1;
         (*new).y = current.y;
         (*new).next = list;
         list = new;
      }

      free(pointer_to_free);
      iterations ++; if (iterations == w*h*bpc*5) break;
   }

   return 0;
}


color imkcolor(int thecolor) {
   color result;

   result.red = (thecolor & 0xff000000) >> 24;
   result.green = (thecolor & 0x00ff0000) >> 16;
   result.blue = (thecolor & 0x0000ff00) >> 8;
   result.alpha = (thecolor & 0x000000ff);

   return result;
}

color mkcolor(int red, char green, char blue, char alpha) {
   int x = 0;
   x |= (red & 0xff) << 24;
   x |= (green & 0xff) << 16;
   x |= (blue & 0xff) << 8;
   x |= (alpha & 0xff);
   return imkcolor(x);
}

int getIndex(int x, int y, int w, int bpc) {
   return y*w*bpc + x*bpc;
}


color getColor(int index, char image[], int bpc) {
   int red, green, blue, alpha;
   red = image[index];
   green = image[index + 1];
   blue = image[index + 2];
   if (bpc == 4) alpha = image[index + 3];

   return mkcolor(red, green, blue, alpha);
}


char compareUsingImage(int x, int y, char image[], int w, int h, int bpc, color target) {
   if (x<0 || x>=w) return 0;
   if (y<0 || y>=h) return 0;

   color current = getColor(getIndex(x, y, w, bpc), image, bpc);

   return compareUsingColor(current, target);
}


char compareUsingColor(color current, color target) {
   if (current.red == target.red &&
      current.green == target.green &&
      current.blue == target.blue)
      return 0xff;
   else
      return 0;
}

color blend(color current, color replacement, int alpha) {
   color result;

   float falpha;
   if (alpha = 255) falpha = 1.;
   else falpha = alpha/255.;

   result.red = (int)(current.red*(1-falpha)) + (int)(replacement.red*falpha);
   result.green = (int)(current.green*(1-falpha)) + (int)(replacement.green*falpha);
   result.blue = (int)(current.blue*(1-falpha)) + (int)(replacement.blue*falpha);
   if (current.alpha == 0)
      result.alpha = replacement.alpha;

   return result;
}

