import zipfile
import rarfile
import os
import xlrd
import ibm_db
import datetime



#遍历压缩文件
def getAllFile(file_path,dst_dir):
    #获取当前路径的父级目录
    #parent_path = os.getcwd()
    #提取文件中的所有文件生成一个列表
    folders = os.listdir(file_path)
    for zip_src in folders:
        unrar_file(os.path.join(file_path,zip_src), dst_dir)


#解压rar文件
def unrar_file(zip_src, dst_dir):
    #判断是否为压缩文件
    rarf = rarfile.RarFile(zip_src)
    rarf.extractall(dst_dir)
    rarf.close()

#解压文件
def unzip_file(zip_src, dst_dir):
    #判断是否为压缩文件
    r = zipfile.is_zipfile(zip_src)
    if r:
        with zipfile.ZipFile(file=zip_src, mode='r') as zf:
             for old_name in zf.namelist():
                 # 由于源码遇到中文是cp437方式，所以解码成gbk，windows即可正常
                 new_name = old_name.encode('cp437').decode('gbk')
                 # 拼接文件的保存路径
                 new_path = os.path.join(dst_dir, new_name)
                 # 是文件，通过open创建文件，写入数据
                 with open(file=new_path, mode='wb') as f:
                    # zf.read 是读取压缩包里的文件内容
                    f.write(zf.read(old_name))
    else:
        print('This is not zip')
#遍历excel
def getAllExcel(dst_dir):
    #获取当前路径的父级目录
    parent_path = os.getcwd()
    #提取文件中的所有文件生成一个列表
    folders = os.listdir(dst_dir)
    for excel in folders:
        print(excel)
        print(dst_dir)
        if os.path.isdir(os.path.join(parent_path,dst_dir,str(excel))) :
            print(excel)
            folders2 = os.listdir(os.path.join(parent_path,dst_dir,str(excel)))
            for excel2 in folders2:
                #print(excel2)  
                if '发布版' in excel2 :
                    print(os.path.join(parent_path,dst_dir,str(excel),str(excel2)))
                    readexcel(os.path.join(parent_path,dst_dir,str(excel),str(excel2)))

def readexcel(excelFile):
    # 打开excel表格
    data_excel = xlrd.open_workbook(excelFile)
    # 通过索引顺序获取sheet
    sheet1_object = data_excel.sheets()[0]
    n_rows = sheet1_object.nrows    # 获取该sheet中的有效行数
    n_cols = sheet1_object.ncols    # 获取该sheet中的有效列数
    #用于存放表字段
    table_list=[]
    #标识是否为同一张表
    table_flag=''
    for i in range(n_rows+1):
        if i == 0 :
            continue
        if i == n_rows :
            make_table(table_list)
            continue
        row_values = sheet1_object.row_values(i)
        if table_flag=='' or row_values[1]==table_flag :
            table_list.append(row_values)
            table_flag=row_values[1]
        else :
            make_table(table_list)
            table_list=[]
            table_flag=''
            table_list.append(row_values)
#构建创表语句
def make_table(table_list):
    #print(table_list)
    table_commit=''
    table_key=''
    table_rename=''
    table_name='CREATE TABLE ' +schema +"."
    table_body=''
    for row_values in table_list :
        if row_values[3] == 'ALL' :
            table_commit+="COMMENT ON TABLE " +schema +"." + row_values[1] + " is ' " + row_values[2] + " '; \n"
        else :
            table_commit+="COMMENT ON COLUMN " +schema +"." +table_rename+ '.' + row_values[3] + " is ' " + str(row_values[4]) + " '; \n"
        if row_values[10] == 'ROWKEY' or row_values[10] == 'Physical Primary Key' :
            table_key+=row_values[3] + ' ,'
        if row_values[3] == 'ALL' :
            table_rename = row_values[0]+'_'+row_values[1]+table_subfix
            table_name+= row_values[0]+'_'+row_values[1]+table_subfix +'( \n'
        elif row_values[10] == 'ROWKEY' or row_values[10] == 'Physical Primary Key' :
            if row_values[5] == 'INTEGER' or row_values[5] == 'DATE' or row_values[5] == 'BIGINT':
                table_body+= row_values[3] + ' ' + row_values[5] +' NOT NULL ,\n'
            elif row_values[5] == 'CHAR' or row_values[5] == 'CHARACTER' or row_values[5] == 'VARCHAR' :
                table_body+= row_values[3] + ' VARCHAR(' + str(int((int(row_values[6])*3+1)/2)) +') NOT NULL ,\n'
            else :
                table_body+= row_values[3] + ' ' + row_values[5] + '(' + str(int(row_values[6])) +') NOT NULL ,\n'
        elif row_values[5] == 'DECIMAL' :
            #print('ssss'+str(row_values[7])+'ssss')
            if '' == str(row_values[7]):
                table_body+= row_values[3] + ' ' + row_values[5] + '(' +str(int(row_values[6])) +','+ '0' +') ,\n'
            else :
                table_body+= row_values[3] + ' ' + row_values[5] + '(' +str(int(row_values[6])) +','+str(int(float(row_values[7]))) +') ,\n'
        elif row_values[5] == 'INTEGER' or row_values[5] == 'DATE' or row_values[5] == 'BIGINT':
            table_body+= row_values[3] + ' ' + row_values[5] +',\n'
        elif row_values[5] == 'CHAR' or row_values[5] == 'CHARACTER' or row_values[5] == 'VARCHAR' :
            table_body+= row_values[3] + ' VARCHAR(' + str(int(int(row_values[6])*3/2)) +') ,\n'
        else :
            table_body+= row_values[3] + ' ' + row_values[5] + '(' + str(int(row_values[6])) +') ,\n'
    table_name+=table_body + ' PRIMARY KEY (' + table_key.strip(',') +'));\n'+table_commit
    #print(table_name)
    #print(table_commit)
    #查看表是否存在
    is_exist=table_exist(table_rename,db2conn)
    #print('is_exist:'+str(is_exist)+ table_rename)
    if is_exist >0 :
        print(table_rename)
        #如果存在表 重命名并创建
        renameTable(table_rename,db2conn)
        #创建表
        createTable(table_name,db2conn)
        #pass

def table_exist(table_rename,db2conn):
    conn = ibm_db.connect(db2conn, "", "")
    sql= "SELECT count(*) FROM syscat.tables WHERE TABNAME = '"+table_rename+"' and TABSCHEMA='"+schema+"' "
    try:
        if conn:
            #print('existconnected')
            #print(sql)
            stmt = ibm_db.exec_immediate(conn, sql)
            rows = ibm_db.fetch_tuple(stmt)
            return rows[0]
    except Exception as ex:
        print('查询表是否存在报错' + table_rename)
        print(ex)
        # 回滚事务
        ibm_db.rollback(conn)
        return 0
    finally:
        # 关闭数据库连接
        ibm_db.close(conn)


def renameTable(table_rename,db2conn):
    dateTime_p = datetime.datetime.now()
    str_p = datetime.datetime.strftime(dateTime_p,'%Y%m%d')
    new_table_name = table_rename+str_p
    conn = ibm_db.connect(db2conn, "", "")
    try:
        if conn:
            renamesql="rename table " +schema + '.' +table_rename + " to " + new_table_name
            #print(renamesql)
            stmt = ibm_db.exec_immediate(conn, renamesql)
            ibm_db.commit(conn)
    except Exception as ex:
        print(ex)
        print('重命名并创建失败' + new_table_name)
        # 回滚事务
        ibm_db.rollback(conn)
    finally:
        # 关闭数据库连接
        ibm_db.close(conn)


def createTable(create_sql,db2conn):

    conn = ibm_db.connect(db2conn, "", "")
    #print('conn')
    try:
        if conn:
            #print('connected')
            stmt = ibm_db.exec_immediate(conn, create_sql)
            rows = ibm_db.num_rows(stmt)
            #print(rows)
            ibm_db.commit(conn)
    except Exception as ex:
        print(ex)
        print('excception')
        # 回滚事务
        ibm_db.rollback(conn)
    finally:
        # 关闭数据库连接
        ibm_db.close(conn)


if __name__ == '__main__':
    #压缩文件路径
    file_path = './file/'
    #解压路径
    dst_dir = './unzipfile'
    db2conn = "DATABASE=KERONG;SCHEMA=SQLG;HOSTNAME=154.43.0.196;PORT=60060;PROTOCOL=TCPIP;UID=db2inst1;PWD=db123@inst123"
    schema = 'SQLJ'
    table_subfix = ''
    getAllFile(file_path,dst_dir)
    #getAllExcel(dst_dir)
    #readexcel('./unzipfile/标准化文档-20220928/数据标准化拆分-综合前端-发布版.xls')
    xxx='''CREATE TABLE BGFWKMSJ(
         KMCADATE DATE,
         KMCABRNO CHAR(6) ,
         KMCACCYC CHAR(3) ,
         KMCAACID CHAR(8) ,
         KMCANM40 CHAR(40) ,
         KMCAAMT DECIMAL(15,2) ); '''
    #createTable(xxx,db2conn)

