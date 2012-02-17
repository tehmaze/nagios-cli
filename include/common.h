#ifndef _COMMON_H_
#define _COMMON_H_

#define OK      0
#define ERROR   2

#ifndef TRUE
#define TRUE    1
#elif (TRUE!=1)
#define TRUE    1
#endif
#ifndef FALSE
#define FALSE   0
#elif (FALSE!=0)
#define FALSE   0
#endif

#ifndef elif
#define elif else if
#endif

#define my_free(ptr) do { if(ptr) { free(ptr); ptr = NULL; } } while(0)

#endif // _COMMON_H_
