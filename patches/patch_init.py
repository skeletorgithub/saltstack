--- a/salt/utils/__init__.py	Tue Jun 20 20:37:23 2017
+++ b/salt/utils/__init__.py	Mon Aug 21 14:11:50 2017
@@ -2461,6 +2461,10 @@
     pkg1 = normalize(pkg1)
     pkg2 = normalize(pkg2)
 
+    if is_sunos():
+       pkg1 = pkg1.split(',',1)[0]
+       pkg2 = pkg2.split(',',1)[0]
+
     try:
         # pylint: disable=no-member
         if distutils.version.LooseVersion(pkg1) < \
@@ -2495,7 +2499,7 @@
     if cmp_func is None:
         cmp_func = version_cmp
 
-    cmp_result = cmp_func(ver1, ver2, ignore_epoch=ignore_epoch)
+    cmp_result = cmp_func(ver1, ver2)
     if cmp_result is None:
         return False
 
