def file_writer(filepath, queue, debug =  False):
    #filepath = filedir + '/' + filename + '_'\
    #    + str(datetime.date.today()) + "-"\
    #    + str(datetime.datetime.now().strftime("%H.%M.%S"))\
    #    + '.csv'
    print("FILEPATH", filepath)
    with open(filepath, 'w') as file:
        while True:
            line = queue.get()  # get a line of text from the queue

            if line is None:    # if none then we are done
                break
            file.write(str(line))
            if debug: print(line,end="")# write it to file
            file.flush()        # flush the buffer
            queue.task_done()   # mark the unit of work complete
    queue.task_done()           # mark the exit signal as processed, after the file was closed
