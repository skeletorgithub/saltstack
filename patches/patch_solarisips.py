--- a/salt/modules/solarisips.py	Tue Jun 20 20:37:23 2017
+++ b/salt/modules/solarisips.py	Tue Aug 22 12:40:21 2017
@@ -303,6 +303,28 @@
     return ''
 
 
+def short_installed_version(name, **kwargs):
+    '''
+    The short installed version of the package in the repository.
+    In case of multiple matches, it returns list of all matched packages.
+    Accepts full or partial FMRI.
+    Please use pkg.latest_version as pkg.available_version is being deprecated.
+
+    CLI Example:
+
+    .. code-block:: bash
+
+        salt '*' pkg.latest_version pkg://solaris/entire
+    '''
+    cmd = '/bin/pkg list -Hv {0}'.format(name)
+    line = __salt__['cmd.run_stdout'](cmd)
+    ret = _ips_get_pkgversion(line).split(',',1)[0]
+
+    if ret:
+        return ret
+    return ''
+
+
 def latest_version(name, **kwargs):
     '''
     The available version of the package in the repository.
@@ -457,9 +479,19 @@
         salt '*' pkg.install pkg://solaris/editor/vim refresh=True
         salt '*' pkg.install pkgs='["foo", "bar"]'
     '''
+
+    name = normalize_name(name)
+    version_pkg = __salt__['pkg.version'](name, **kwargs)
+    latest_pkg = __salt__['pkg.latest_version'](name, **kwargs)
+
+    if is_installed(name):
+        short_installed_pkg = short_installed_version(name, **kwargs)
+    else:
+        short_installed_pkg = ''
+
     if not pkgs:
-        if is_installed(name):
-            return 'Package already installed.'
+        if is_installed(name) and (version_pkg.get(name) == latest_pkg.get(name) or short_installed_pkg == version):
+            return {name:'Package already installed.'}
 
     if refresh:
         refresh_db(full=True)
@@ -484,7 +516,10 @@
         else:
             pkg2inst = "{0}".format(name)
 
-    cmd = 'pkg install -v --accept '
+    if is_installed(name) and (salt.utils.version_cmp(version,short_installed_pkg) == -1):
+        cmd = 'pkg update -v --accept '
+    else:
+        cmd = 'pkg install -v --accept '
     if test:
         cmd += '-n '
 
@@ -597,3 +632,74 @@
         salt '*' pkg.purge <package name>
     '''
     return remove(name, **kwargs)
+
+
+def update(name=None, pkgs=None, **kwargs):
+    '''
+    Update specified package. Accepts full or partial FMRI.
+    In case of multiple match, the command fails and won't modify the OS.
+
+    name
+        The name of the package to be deleted.
+
+
+    Multiple Package Options:
+
+    pkgs
+        A list of packages to update. Must be passed as a python list. The
+        ``name`` parameter will be ignored if this option is passed.
+
+
+    Returns a list containing the updated packages.
+
+    CLI Example:
+
+    .. code-block:: bash
+
+        salt '*' pkg.update <package name>
+        salt '*' pkg.update tcsh
+        salt '*' pkg.update pkg://solaris/shell/tcsh
+        salt '*' pkg.update pkgs='["foo", "bar"]'
+    '''
+    pkg2udp = ''
+    if pkgs:    # multiple packages specified
+        for pkg in pkgs:
+            pkg2upd += '{0} '.format(pkg)
+        log.debug(
+            'Installing these packages instead of {0}: {1}'.format(
+                name, pkg2upd
+            )
+        )
+    else:   # update single package
+        pkg2upd = '{0}'.format(name)
+
+    # Get a list of the currently installed pkgs.
+    old = list_pkgs()
+
+    # Remove the package(s)
+    cmd = '/bin/pkg update --accept -v {0}'.format(pkg2upd)
+    out = __salt__['cmd.run_all'](cmd, output_loglevel='trace')
+
+    # Get a list of the packages after the uninstall
+    __context__.pop('pkg.list_pkgs', None)
+    new = list_pkgs()
+    ret = salt.utils.compare_dicts(old, new)
+
+    if out['retcode'] == 4:
+        return {'name': name,
+                'changes': '',
+                'result': True,
+                'comment': 'No updates available for this image.'}
+
+    elif out['retcode'] != 0:
+        raise CommandExecutionError(
+            'Error occurred updating package(s)',
+            info={
+                'changes': ret,
+                'retcode': ips_pkg_return_values[out['retcode']],
+                'errors': [out['stderr']]
+            }
+        )
+
+    return ret
+
