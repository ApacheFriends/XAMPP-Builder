"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
"""
import re

def swapKeyValue(dict):
    for key in dict.copy():
        if dict[key] in dict:
            dict[dict[key]].append(key)
        else:
            dict[dict[key]] = [key]
        del dict[key]
    return dict

def differencesBetweenDigests(source_files, target_files, moved_files=None):
    if moved_files is None:
        moved_files = ()

    result = {
        'changed':[],
        'moved':[],
        'symlinks':[],
        'removed':[],
        'copied':[],
        'new':[]
    }

    #find all removed and changed files
    for file in source_files.copy():
        if file not in target_files:
            result['removed'].append(file)
        elif target_files[file] != source_files[file]:
            result['changed'].append({'file':file, 'source_digest':source_files[file], 'target_digest':target_files[file]})
            # Remove them from our array, because they are handled and so
            # we avoid that we later work with them again.
            del source_files[file]
            del target_files[file]

    # find all newly added files
    for file in target_files:
        if file not in source_files:
            result['new'].append(file)

    # Ok, that was the supid part, now we make the intelegent things

    # First we look up, what we have as input for moved files.
    # If we have a mach the files are removed from source_files
    # and target_files so, that we do not have to care later, because they
    # were already handled.
    for pattern, replacement in moved_files:
        r = re.compile(pattern)
        for file in source_files.copy():
            new_file = re.sub(r, replacement, file)

            if new_file is not file and \
                new_file not in source_files and \
                new_file in target_files:

                result['moved'].append({'from':file, 'to':new_file})
                result['removed'].remove(file)
                result['new'].remove(new_file)
                if source_files[file] != target_files[new_file]:
                    result['changed'].append({'file':new_file, 'source_digest':source_files[file], 'target_digest':target_files[new_file]})

    # First we search for files that have not be changed but moved
    #  to do that, we switch the keys and values of source_files and
    #  target_files
    source_digests = swapKeyValue(source_files.copy())
    target_digests = swapKeyValue(target_files.copy())

    for digest in source_digests:
        # This means there are two or more files with the same content
        if digest in target_digests:
            sources = source_digests[digest][:]
            targets = target_digests[digest][:]

            to_not_remove = []
            to_be_not_new = []

            # Ok, first case. In either, the target and the source, exists
            # in each case one file with the same digest, but it path is
            # different
            if len(sources) == 1 and len(targets) == 1:
                if sources[0] != targets[0]:
                    result['moved'].append({'from': sources[0], 'to':targets[0]})
                    to_not_remove.append(sources[0])
                    to_be_not_new.append(targets[0])
            # Ok now we first remove all path's that occours in both.
            else:
                for path in sources[:]:
                    if path in targets:
                        sources.remove(path)
                        targets.remove(path)

                # Ok now we can make conflict resolution
                if len(sources) < len(targets):
                    for i in range(len(sources)):
                        result['moved'].append({'from': sources[i], 'to': targets[i]})
                        to_not_remove.append(sources[i])
                        to_be_not_new.append(targets[i])
                    # Oh there is an additional copy of an existing file
                    i = len(targets) - len(sources)
                    source = source_digests[digest][0]
                    for file in targets[i:]:
                        result['copied'].append({'from':source, 'to':file, 'digest':digest})
                        to_be_not_new.append(file)
                elif len(sources) > len(targets):
                    for i in range(len(targets)):
                        result['moved'].append({'from': sources[i], 'to': targets[i]})
                        to_not_remove.append(sources[i])
                        to_be_not_new.append(targets[i])
                elif len(sources) == len(targets):
                    for i in range(len(sources)):
                        result['moved'].append({'from': sources[i], 'to': targets[i]})
                        to_not_remove.append(sources[i])
                        to_be_not_new.append(targets[i])
                else:
                    # Do we really need this case? All should be handeled I think.
                    raise StandardError('Case not handeled %s <=> %s' % (sources, targets))

            for file in to_not_remove:
                try:
                    result['removed'].remove(file)
                except:
                    pass

            for file in to_be_not_new:
                try:
                    result['new'].remove(file)
                except:
                    pass
    return result