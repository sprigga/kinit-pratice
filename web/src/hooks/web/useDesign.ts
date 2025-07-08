import variables from '@/styles/variables.module.less'

export const useDesign = () => {
  const lessVariables = variables

  /**
   * @param scope 類名
   * @returns 返回空間名-類名
   */
  const getPrefixCls = (scope: string) => {
    return `${lessVariables.namespace}-${scope}`
  }

  return {
    variables: lessVariables,
    getPrefixCls
  }
}
