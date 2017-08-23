--- a/salt/states/pkg.py	Tue Jun 20 20:37:23 2017
+++ b/salt/states/pkg.py	Tue Aug 22 12:39:43 2017
@@ -1850,6 +1850,13 @@
                                                fromrepo=fromrepo,
                                                refresh=refresh,
                                                **kwargs)
+
+        if avail and _find_install_targets(name):
+            return __salt__['pkg.update'](name,pkgs, **kwargs)
+       
+        elif avail and not pkgs:
+            desired_pkgs = [[key for key, value in avail.items() if desired_pkgs[0] in key][0]]
+
     except CommandExecutionError as exc:
         return {'name': name,
                 'changes': {},
@@ -1957,12 +1964,15 @@
                     'comment': 'An error was encountered while installing '
                                'package(s): {0}'.format(exc)}
 
+        if isinstance(changes,str):
+            changes = eval(changes)
+
         if changes:
             # Find failed and successful updates
             failed = [x for x in targets
                       if not changes.get(x) or
-                      changes[x].get('new') != targets[x] and
-                      targets[x] != 'latest']
+                      isinstance((changes[x]),dict) and changes[x].get('new') != targets[x] and
+                      targets[x] != 'latest' and x not in up_to_date]
             successful = [x for x in targets if x not in failed]
 
             comments = []
