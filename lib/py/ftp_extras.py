import ftplib
import traceback


def ftp_rmr(ftp, path, logger):
    wd = ftp.pwd()

    try:
        names = ftp.nlst(path)
    except ftplib.all_errors as error:
        logger.error(f"Failed to list {path}: {error}")
        logger.debug(traceback.format_exc())
        return

    for name in names:
        try:
            ftp.cwd(name)
            ftp.cwd(wd)
            ftp_rmr(ftp, name, logger)
        except ftplib.all_errors:
            try:
                ftp.delete(name)
                logger.debug(f"Deleted file: {name}")
                logger.debug(traceback.format_exc())
            except ftplib.all_errors as error:
                logger.error(f"Failed to delete file: {name}: {error}")
                logger.debug(traceback.format_exc())

    try:
        ftp.rmd(path)
        logger.info(f"Deleted {path}.")
    except ftplib.all_errors as error:
        logger.error(f"Failed to delete {path}: {error}")
        logger.debug(traceback.format_exc())


def ftp_mkdirp(ftp, path):
    dirs, parent = path.split("/"), "./"
    for d in dirs:
        try:
            ftp.mkd(parent + "/" + d)
        except ftplib.error_perm:
            pass
        parent = parent + "/" + d
