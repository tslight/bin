#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <ctype.h>
  
static void
list(char* dir)
{
	DIR* d;
	struct dirent* dp;
	if (!(d = opendir(dir))) return;
	while ((dp = readdir(d)) != NULL) {
		ulong namelen = strlen(dp->d_name);
		if (dp->d_type == DT_DIR) {
			if ((strcmp(dp->d_name, ".") == 0) ||
			    (strcmp(dp->d_name, "..") == 0)) continue;
			char p[1024];
			snprintf(p, sizeof(p), "%s/%s", dir, dp->d_name);
			list(p);
		}
		else if ((isdigit(dp->d_name[namelen-1])) &&
			 (dp->d_name[namelen-2] == '.')) {
			write(1, dp->d_name, namelen-2);
			write(1, "\n", 1);
		}
	}
	closedir(d);
}
  
int
main(void)
{
	char* path = getenv("MANPATH");
	char* dir;
	for (dir = strsep(&path, ":"); dir != NULL; dir = strsep(&path, ":"))
		list(dir);
	return 0;
}
